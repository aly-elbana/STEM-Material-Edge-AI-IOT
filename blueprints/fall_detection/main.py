"""Fall detection for elderly people (medical pathway, wearable at the waist).

Classic physics baseline: FREE-FALL (|a| << 1 g) -> IMPACT (|a| >> 1 g) -> STILLNESS.
AI upgrade: record many activities (walk, sit down fast, jump, lie down, SAFE falls onto a
mattress with a dummy or yourself under supervision), window them, train a classifier,
and show it beats the threshold rule on a locked test set.

    python -m blueprints.fall_detection.main                 # threshold baseline
    python -m blueprints.fall_detection.main --model models/fall
A 15-second cancel button (GPIO5) prevents false alarms reaching the family.
"""
import argparse
import collections
import time

import pandas as pd

from common import SIMULATE
from common.alerts import LocalAlarm, telegram
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog
from sensors import mpu6050

G = 9.81
p = argparse.ArgumentParser()
p.add_argument("--model")
p.add_argument("--rate", type=float, default=50)
p.add_argument("--cancel-s", type=float, default=15)
p.add_argument("--topic", default="stem/team00/fall1/status")
a = p.parse_args()

alarm, mq, lat = LocalAlarm(27), EdgeMQTT("fall1"), LatencyLog("fall_latency.csv")
cancelled = {"v": False}
if not SIMULATE:
    from sensors.digital_inputs import button
    button(5, on_press=lambda: cancelled.update(v=True))
model = None
if a.model:
    from ml.tabular.predict_live import LiveModel
    from ml.timeseries.features import make_windows
    model = LiveModel(a.model)
buf = collections.deque(maxlen=int(a.rate * 2))     # last 2 seconds


def rule_fall(win):
    mags = [((r["ax"] ** 2 + r["ay"] ** 2 + r["az"] ** 2) ** 0.5) / G for r in win]
    for i, m in enumerate(mags):
        if m < 0.4:                                     # free fall
            after = mags[i:i + int(a.rate * 0.6)]
            if after and max(after) > 2.5:              # impact within 0.6 s
                tail = mags[-int(a.rate * 0.5):]
                if max(tail) - min(tail) < 0.3:         # lying still afterwards
                    return True
    return False


period, nxt, step = 1 / a.rate, time.perf_counter(), 0
while True:
    r = mpu6050.read()
    if SIMULATE and step % 500 == 400:                 # inject a fall pattern sometimes
        for m in [0.2] * 10 + [3.2] * 3 + [1.0] * 40:
            buf.append({"ax": 0, "ay": 0, "az": m * G, "gx": 0, "gy": 0, "gz": 0})
    buf.append(r)
    step += 1
    if len(buf) == buf.maxlen and step % int(a.rate / 2) == 0:   # check twice a second
        t0 = lat.start()
        win = list(buf)
        if model:
            feats = make_windows(pd.DataFrame(win), ["ax", "ay", "az"], a.rate, 2.0, 2.0).iloc[0].to_dict()
            fall = model.predict(feats)[0] == "fall"
        else:
            fall = rule_fall(win)
        if fall:
            lat.stop(t0, "fall")
            alarm.beep(5)
            print("FALL detected - press the button within", a.cancel_s, "s to cancel")
            cancelled["v"] = False
            end = time.time() + (2 if SIMULATE else a.cancel_s)
            while time.time() < end and not cancelled["v"]:
                time.sleep(0.1)
            if not cancelled["v"]:
                telegram("Possible FALL detected - please check now.")
                mq.publish(a.topic, {"ts": round(time.time(), 2), "event": "fall"})
            buf.clear()
            nxt = time.perf_counter()        # resume steady sampling after the alert
    nxt += period
    time.sleep(max(0, nxt - time.perf_counter()))
