"""Lab E: one loop - SENSE, THINK, ACT, REPORT.

SIMULATE = True  -> runs on any laptop (fake readings, buzzer = print).
SIMULATE = False -> Raspberry Pi with a buzzer on GPIO27 (pin 13);
                    replace read_sensors() with your real sensors from Part 1.
The buzzer never waits for the network: the local decision comes first.
"""
import time, json, random
import pandas as pd
from sklearn.covariance import EllipticEnvelope
from m3_common import FEATURES, fake_reading

SIMULATE = True
STEPS = 30            # how many loop steps (use while True on the real device)

if SIMULATE:
    class Buzzer:
        def __init__(self, pin): self.value = False
else:
    from gpiozero import Buzzer
buzzer = Buzzer(27)

model = EllipticEnvelope(contamination=0.01).fit(
    pd.read_csv("m3_normal.csv")[FEATURES])


def read_sensors():
    # Simulated: every 10th reading is a fault
    return fake_reading("bearing" if random.random() < 0.1 else None)


def publish_status(anomaly, x, ms):
    online = random.random() > 0.2          # pretend the internet drops 20% of the time
    if not online:
        raise ConnectionError("no internet")
    print("   REPORT ->", json.dumps({"anomaly": bool(anomaly), "x": x, "ms": round(ms, 2)}))


def log_locally(e):
    with open("offline_log.txt", "a") as f:
        f.write(f"{time.time()} {e}\n")
    print("   (offline - saved locally)")


for _ in range(STEPS):
    x = read_sensors()                                   # SENSE
    t0 = time.perf_counter()
    anomaly = model.predict(pd.DataFrame([x], columns=FEATURES))[0] == -1   # THINK
    buzzer.value = anomaly                               # ACT, even with no internet
    ms = (time.perf_counter() - t0) * 1000
    print(x, "BUZZ!" if anomaly else "ok", f"{ms:.1f} ms")
    try:
        publish_status(anomaly, x, ms)                   # REPORT when online
    except Exception as e:
        log_locally(e)
    time.sleep(0.2)
