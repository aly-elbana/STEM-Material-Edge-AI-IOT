"""Bonus: not every famous model fits your data. TEST before you trust.

We generate 500 readings of each fault and count how many each detector catches.
On M3's data, IsolationForest misses many faults where only ONE sensor goes
wrong; EllipticEnvelope and LocalOutlierFactor catch almost all of them.
Note: EllipticEnvelope assumes ONE "normal" cluster. If your machine has several
normal modes (idle / running), try LocalOutlierFactor instead.
"""
import random
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from m3_common import FEATURES, fake_reading

X = pd.read_csv("m3_normal.csv")[FEATURES]
random.seed(1)
tests = {f or "normal": pd.DataFrame([fake_reading(f) for _ in range(500)], columns=FEATURES)
         for f in [None, "bearing", "overheat", "overload"]}

models = {
    "IsolationForest": IsolationForest(contamination=0.01, random_state=42),
    "EllipticEnvelope": EllipticEnvelope(contamination=0.01),
    "LocalOutlierFactor": make_pipeline(StandardScaler(),
                                        LocalOutlierFactor(novelty=True, contamination=0.01)),
}
print(f"{'flagged as anomaly':20}" + "".join(f"{k:>11}" for k in tests))
for name, m in models.items():
    m.fit(X)
    rates = [(m.predict(d) == -1).mean() for d in tests.values()]
    print(f"{name:20}" + "".join(f"{r:>11.0%}" for r in rates))
print("\n'normal' column = false alarms (want LOW). Fault columns = caught (want HIGH).")
