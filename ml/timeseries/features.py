"""Turn a stream of samples (vibration, accelerometer, sound level, current...)
into windows of features a normal ML model can learn from.

Why: one sample says little. A 1-second window says a lot:
  rms (energy), peak, crest factor, kurtosis (spikes = bearing damage),
  and FFT band energies (WHICH frequencies are shaking).

    python -m ml.timeseries.features raw.csv --cols ax ay az --rate 200 --window 1.0 --label label
-> writes raw_features.csv, ready for ml.tabular.train_tabular
"""
import argparse

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew


def window_features(x, rate, bands=((0, 10), (10, 30), (30, 60), (60, 100))):
    x = np.asarray(x, dtype=float)
    x = x - x.mean()                      # remove gravity / DC offset
    rms = np.sqrt(np.mean(x ** 2))
    peak = np.max(np.abs(x))
    f = {"mean_abs": np.mean(np.abs(x)), "std": x.std(), "rms": rms, "peak": peak,
         "crest": peak / (rms + 1e-9), "kurtosis": kurtosis(x), "skew": skew(x),
         "zero_cross": np.mean(np.diff(np.sign(x)) != 0)}
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / rate)
    total = spec.sum() + 1e-9
    for lo, hi in bands:
        m = (freqs >= lo) & (freqs < hi)
        f[f"band_{lo}_{hi}"] = spec[m].sum() / total
    f["dominant_hz"] = freqs[np.argmax(spec[1:]) + 1] if len(spec) > 1 else 0.0
    return f


def make_windows(df, cols, rate, window_s=1.0, step_s=0.5, label=None):
    n, step = int(rate * window_s), int(rate * step_s)
    rows = []
    for start in range(0, len(df) - n + 1, step):
        seg = df.iloc[start:start + n]
        row = {}
        for c in cols:
            for k, v in window_features(seg[c].values, rate).items():
                row[f"{c}_{k}"] = v
        if label:   # the most common label inside the window
            row[label] = seg[label].mode().iloc[0]
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--cols", nargs="+", required=True)
    p.add_argument("--rate", type=float, required=True, help="samples per second")
    p.add_argument("--window", type=float, default=1.0)
    p.add_argument("--step", type=float, default=0.5)
    p.add_argument("--label")
    a = p.parse_args()
    out = make_windows(pd.read_csv(a.csv), a.cols, a.rate, a.window, a.step, a.label)
    path = a.csv.replace(".csv", "_features.csv")
    out.to_csv(path, index=False)
    print(f"{len(out)} windows x {out.shape[1]} columns -> {path}")
