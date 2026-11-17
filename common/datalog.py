"""Log readings to CSV with a timestamp on every row (your dataset + your logbook).

    log = CSVLogger("data/run_01.csv", ["temp", "humidity", "label"])
    log.write(temp=24.1, humidity=51, label="normal")
"""
import csv
import os
import time


class CSVLogger:
    def __init__(self, path, fields):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.fields = ["timestamp"] + list(fields)
        new = not os.path.exists(path)
        self._f = open(path, "a", newline="")
        self._w = csv.DictWriter(self._f, fieldnames=self.fields, extrasaction="ignore")
        if new:
            self._w.writeheader()

    def write(self, **values):
        values.setdefault("timestamp", round(time.time(), 3))
        self._w.writerow(values)
        self._f.flush()

    def close(self):
        self._f.close()
