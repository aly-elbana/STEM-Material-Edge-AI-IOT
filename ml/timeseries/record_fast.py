"""Record a sensor at a steady rate (e.g. MPU6050 at 200 Hz) to CSV, with a label.

    python -m ml.timeseries.record_fast --label normal --seconds 60 --rate 200
    python -m ml.timeseries.record_fast --label unbalanced --seconds 60 --rate 200

Python on Linux is not real-time: the script records the REAL time of each sample
and prints the achieved rate. Use that rate in features.py.
"""
import argparse
import time

from common.datalog import CSVLogger
from sensors import mpu6050

p = argparse.ArgumentParser()
p.add_argument("--label", required=True)
p.add_argument("--seconds", type=float, default=30)
p.add_argument("--rate", type=float, default=200)
p.add_argument("--out", default="data/vibration.csv")
a = p.parse_args()

log = CSVLogger(a.out, ["ax", "ay", "az", "gx", "gy", "gz", "label"])
period, n = 1.0 / a.rate, 0
t_end = time.perf_counter() + a.seconds
next_t = time.perf_counter()
start = next_t
while time.perf_counter() < t_end:
    r = mpu6050.read()
    log.write(timestamp=round(time.time(), 4), label=a.label, **r)
    n += 1
    next_t += period
    time.sleep(max(0.0, next_t - time.perf_counter()))
print(f"{n} samples, achieved {n / (time.perf_counter() - start):.1f} Hz -> {a.out}")
