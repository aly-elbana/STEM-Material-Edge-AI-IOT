"""Lab A: learn what "normal" looks like, then flag anything strange.

Trained on NORMAL data only -> no failure data needed to start.
EllipticEnvelope draws an "ellipse" around the normal readings
(the dashed ellipse on slide 10). Anything outside it = alarm.
Run 00_make_data.py first.
"""
import pandas as pd
from sklearn.covariance import EllipticEnvelope

df = pd.read_csv("m3_normal.csv")          # logged like Part 1
X = df[["temp", "vibration", "current"]]

model = EllipticEnvelope(contamination=0.01).fit(X)

tests = pd.DataFrame([[32.1, 0.61, 4.2],   # looks normal
                      [32.2, 0.95, 4.2],   # only the vibration is odd
                      [36.2, 0.91, 4.8]],  # hot + shaking + high current
                     columns=X.columns)
for row, p in zip(tests.values.tolist(), model.predict(tests)):
    print(row, "->", "normal" if p == 1 else "ANOMALY")   # 1 = normal, -1 = anomaly

# Try it: change the numbers above. At what temperature does it start to worry?
