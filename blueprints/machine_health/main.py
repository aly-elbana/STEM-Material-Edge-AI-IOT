"""Machine health / predictive maintenance (the M3 example, for real).

Sensors: MPU6050 (vibration) + INA219 (motor current) + MLX90614 (surface temperature).
Model: anomaly detection on 1-second vibration windows (trained on NORMAL running only).

Step 1 - record normal running: at least 5 minutes in total, in several sessions
    (different loads/days) -> 600+ windows:
    python -m blueprints.machine_health.main record --label normal --seconds 300
Step 2 - (optional) record SAFE simulated faults for testing: small weight taped on the fan
    blade (unbalance), loosened mount, blocked airflow:
    python -m blueprints.machine_health.main record --label unbalance --seconds 120
Step 3 - features + model:
    python -m ml.timeseries.features data/machine.csv --cols ax ay az --rate 200 --label label
    python -m ml.tabular.train_tabular data/machine_features.csv --mode anomaly --model lof \
        --test data/machine_features.csv --target label --out models/machine
Step 4 - run live:
    python -m blueprints.machine_health.main run --model models/machine
"""
import argparse
import time

import pandas as pd

from common.alerts import LocalAlarm
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog
from ml.timeseries.features import make_windows
from sensors import ina219_current, mlx90614_ir_temp, mpu6050

p = argparse.ArgumentParser()
p.add_argument("mode", choices=["record", "run"])
p.add_argument("--label", default="normal")
p.add_argument("--seconds", type=float, default=60)
p.add_argument("--rate", type=float, default=200)
p.add_argument("--model", default="models/machine")
p.add_argument("--topic", default="stem/team00/motor1/status")
a = p.parse_args()


def grab_window(seconds, rate):
    rows, period = [], 1.0 / rate
    nxt = time.perf_counter()
    end = nxt + seconds
    while time.perf_counter() < end:
        rows.append(mpu6050.read())
        nxt += period
        time.sleep(max(0, nxt - time.perf_counter()))
    return pd.DataFrame(rows)


if a.mode == "record":
    log = CSVLogger("data/machine.csv", ["ax", "ay", "az", "label"])
    n = 0
    end = time.time() + a.seconds
    while time.time() < end:
        df = grab_window(1.0, a.rate)
        for r in df.to_dict("records"):
            log.write(ax=r["ax"], ay=r["ay"], az=r["az"], label=a.label)
        n += len(df)
    print(f"recorded {n} samples ({a.label}) -> data/machine.csv")
else:
    from ml.tabular.predict_live import LiveModel
    model = LiveModel(a.model)
    alarm, mq, lat = LocalAlarm(27), EdgeMQTT("motor1"), LatencyLog("machine_latency.csv")
    bad_streak = 0
    try:
        while True:
            df = grab_window(1.0, a.rate)                     # SENSE (1 s of vibration)
            t0 = lat.start()
            feats = make_windows(df, ["ax", "ay", "az"], a.rate, 1.0, 1.0).iloc[0].to_dict()
            state, _ = model.predict(feats)                   # THINK
            bad_streak = bad_streak + 1 if state == "anomaly" else 0
            alarm.set(bad_streak >= 2)                        # ACT (2 windows in a row = fewer false alarms)
            ms = lat.stop(t0, state)
            msg = {"ts": round(time.time(), 2), "state": state, "streak": bad_streak,
                   "rms": round(feats["az_rms"], 4), "think_ms": round(ms, 1),
                   **ina219_current.read(), **mlx90614_ir_temp.read()}
            mq.publish(a.topic, msg)                          # REPORT
            print(msg)
    except KeyboardInterrupt:
        print("\n", lat.summary())
        mq.close()
