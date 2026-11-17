"""Merge sensor logs that were recorded SEPARATELY (different devices, different
rates, different column names / units / label names) into one training table.

Typical problems this fixes:
  * Pi A logs temperature every 1 s, Pi B logs vibration 50x per second
    -> align on time with merge_asof (nearest earlier reading, max gap tolerance)
  * one file says "temp", another "Temperature_C", another is in Fahrenheit
  * one team labelled "ok/bad", another "normal/fault"

    python -m ml.datasets.merge_sensor_csvs config.json --out merged.csv
config.json:
{
  "base": {"file": "vibration.csv", "rename": {"accel_rms": "vib_rms"}},
  "others": [
    {"file": "temp.csv", "rename": {"Temperature_F": "temp_c"},
     "convert": {"temp_c": "f_to_c"}, "tolerance_s": 2}
  ],
  "label_column": "label",
  "label_map": {"ok": "normal", "bad": "fault", "Normal": "normal"}
}
"""
import argparse
import json

import pandas as pd

CONVERT = {"f_to_c": lambda s: (s - 32) * 5 / 9, "mv_to_v": lambda s: s / 1000.0,
           "ms_to_s": lambda s: s / 1000.0}


def load(spec):
    df = pd.read_csv(spec["file"]).rename(columns=spec.get("rename", {}))
    for col, how in spec.get("convert", {}).items():
        df[col] = CONVERT[how](df[col])
    ts = df["timestamp"]
    # numbers = UNIX seconds (what common/datalog.py writes); text = "2026-11-17 10:00:00"
    ts = pd.to_datetime(ts.astype(float), unit="s") if pd.api.types.is_numeric_dtype(ts) else pd.to_datetime(ts)
    df["timestamp"] = ts.astype("datetime64[ns]")      # same resolution for every file
    return df.sort_values("timestamp")


p = argparse.ArgumentParser()
p.add_argument("config")
p.add_argument("--out", default="merged.csv")
a = p.parse_args()
cfg = json.load(open(a.config))
merged = load(cfg["base"])
for spec in cfg.get("others", []):
    other = load(spec)
    merged = pd.merge_asof(merged, other, on="timestamp", direction="backward",
                           tolerance=pd.Timedelta(seconds=spec.get("tolerance_s", 1)),
                           suffixes=("", "_" + spec["file"].split(".")[0]))
lab = cfg.get("label_column")
if lab and lab in merged:
    merged[lab] = merged[lab].replace(cfg.get("label_map", {}))
before = len(merged)
merged = merged.dropna()
print(f"rows: {before} -> {len(merged)} after dropping rows with gaps")
if lab and lab in merged:
    print(merged[lab].value_counts().to_string())
merged.to_csv(a.out, index=False)
print("saved", a.out)
