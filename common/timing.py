"""Measure response time the way the capstone asks: input -> output, many runs.

    lat = LatencyLog("response_times.csv")
    t = lat.start()
    ... read sensor, run model, act ...
    lat.stop(t, note="anomaly")      # one row per event
    print(lat.summary())             # mean / p95 / worst, in ms
"""
import csv
import os
import statistics
import time


class LatencyLog:
    def __init__(self, path="response_times.csv"):
        self.path = path
        self.values = []
        new = not os.path.exists(path)
        self._f = open(path, "a", newline="")
        self._w = csv.writer(self._f)
        if new:
            self._w.writerow(["timestamp", "latency_ms", "note"])

    @staticmethod
    def start():
        return time.perf_counter()

    def stop(self, t0, note=""):
        ms = (time.perf_counter() - t0) * 1000.0
        self.values.append(ms)
        self._w.writerow([round(time.time(), 3), round(ms, 3), note])
        self._f.flush()
        return ms

    def summary(self):
        v = sorted(self.values)
        if not v:
            return "no samples yet"
        p95 = v[min(len(v) - 1, int(0.95 * len(v)))]
        return (f"n={len(v)}  mean={statistics.mean(v):.1f} ms  "
                f"p95={p95:.1f} ms  worst={v[-1]:.1f} ms")


def benchmark(fn, runs=50, warmup=5):
    """Time any function (e.g. one model prediction). Returns dict in ms."""
    for _ in range(warmup):
        fn()
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    return {"runs": runs, "mean_ms": statistics.mean(times),
            "p95_ms": times[int(0.95 * (runs - 1))], "worst_ms": times[-1]}
