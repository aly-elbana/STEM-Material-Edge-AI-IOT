"""Sensor calibration in 3 steps (a capstone requirement):
  1. Put your sensor next to a REFERENCE instrument (lab thermometer, ruler, scale,
     pH buffer 4/7/10, phone lux meter...). Write pairs in a CSV:
        sensor,reference
        24.9,24.0
        30.4,29.6 ...   (5-10 points over the whole range you need)
  2. python -m calibration.calibrate pairs.csv --name temp
     -> fits  reference = a * sensor + b , prints error before/after, saves
        calibration/temp.json and calibration/temp_plot.png  (logbook!)
  3. In your code:
        from calibration.calibrate import Calibration
        cal = Calibration.load("temp");  true_value = cal(raw_value)
--degree 2 for curved sensors (LDR, some gas sensors).
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


class Calibration:
    def __init__(self, coeffs):
        self.coeffs = list(coeffs)

    def __call__(self, x):
        return float(np.polyval(self.coeffs, x))

    @classmethod
    def load(cls, name):
        return cls(json.load(open(os.path.join(HERE, f"{name}.json")))["coeffs"])


if __name__ == "__main__":
    import pandas as pd
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--name", required=True)
    p.add_argument("--degree", type=int, default=1)
    a = p.parse_args()
    d = pd.read_csv(a.csv)
    s, r = d["sensor"].values, d["reference"].values
    coeffs = np.polyfit(s, r, a.degree)
    fixed = np.polyval(coeffs, s)
    before, after = np.abs(s - r), np.abs(fixed - r)
    print("fit:", " ".join(f"{c:+.5f}" for c in coeffs))
    print(f"error BEFORE: mean {before.mean():.3f}  max {before.max():.3f}")
    print(f"error AFTER : mean {after.mean():.3f}  max {after.max():.3f}")
    json.dump({"coeffs": coeffs.tolist(), "degree": a.degree,
               "mean_abs_error_before": float(before.mean()), "mean_abs_error_after": float(after.mean())},
              open(os.path.join(HERE, f"{a.name}.json"), "w"), indent=2)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs = np.linspace(s.min(), s.max(), 100)
    plt.figure(figsize=(6, 4.5))
    plt.plot(s, r, "o", label="measured pairs")
    plt.plot(xs, np.polyval(coeffs, xs), "-", label="correction")
    plt.plot(xs, xs, "--", color="gray", label="perfect sensor (y = x)")
    plt.xlabel("sensor reading"); plt.ylabel("reference"); plt.legend(); plt.title(a.name)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, f"{a.name}_plot.png"), dpi=150)
    print("saved", f"calibration/{a.name}.json and {a.name}_plot.png")
