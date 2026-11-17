"""Use a model trained by train_tabular.py on live readings (on the Pi).

    from ml.tabular.predict_live import LiveModel
    m = LiveModel("models")
    label, ms = m.predict({"temp": 31.2, "vibration": 0.62, "current": 4.1})
"""
import json
import os
import time

import joblib
import pandas as pd


class LiveModel:
    def __init__(self, folder="models"):
        self.model = joblib.load(os.path.join(folder, "model.joblib"))
        meta = json.load(open(os.path.join(folder, "features.json")))
        self.features, self.mode = meta["features"], meta["mode"]

    def predict(self, reading: dict):
        x = pd.DataFrame([[reading[f] for f in self.features]], columns=self.features)
        t0 = time.perf_counter()
        out = self.model.predict(x)[0]
        ms = (time.perf_counter() - t0) * 1000
        if self.mode == "anomaly":
            out = "normal" if out == 1 else "anomaly"
        return out, ms

    def proba(self, reading: dict):
        x = pd.DataFrame([[reading[f] for f in self.features]], columns=self.features)
        if hasattr(self.model, "predict_proba"):
            return dict(zip(self.model.classes_, self.model.predict_proba(x)[0]))
        return {}
