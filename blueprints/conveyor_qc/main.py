"""Conveyor quality control: count, inspect, reject, report.

Hardware: DC gear motor + driver (belt), IR break-beam (detect item), camera above the
belt (or TCS34725 colour sensor), servo pusher (or solenoid) to reject, optional
encoder for belt speed. See README.md for wiring and the requirements to measure.

    python -m blueprints.conveyor_qc.main                     # simulation
    SIMULATE=0 python -m blueprints.conveyor_qc.main --model models/image/model_fp16.tflite \
        --labels models/image/labels.txt --bad cap_missing dented
"""
import argparse
import queue
import threading
import time

from common import SIMULATE
from common.camera import Camera
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog
from motors.dc_motor import DCMotor
from motors.servo import Servo
from sensors.digital_inputs import object_counter

p = argparse.ArgumentParser()
p.add_argument("--model", help=".tflite classifier (else: simulated / colour rule)")
p.add_argument("--labels")
p.add_argument("--bad", nargs="*", default=["defective"], help="class names to reject")
p.add_argument("--min-conf", type=float, default=0.8)
p.add_argument("--speed", type=float, default=0.5, help="belt motor speed 0..1")
p.add_argument("--travel-s", type=float, default=0.6,
               help="seconds from the camera/beam to the pusher (measure it!)")
p.add_argument("--topic", default="stem/team00/belt1")
a = p.parse_args()

belt, pusher = DCMotor(), Servo(pin=18)
cam = Camera((640, 480))
mq = EdgeMQTT("belt1")
lat = LatencyLog("conveyor_latency.csv")
log = CSVLogger("data/conveyor.csv", ["label", "conf", "rejected", "latency_ms"])
stats = {"total": 0, "rejected": 0, "start": time.time()}
items = queue.Queue()

clf = None
if a.model:
    from ml.image.classify_live import TFLiteClassifier
    clf = TFLiteClassifier(a.model, a.labels)


def classify(frame):
    if clf:
        return clf.predict(frame)[:2]
    if SIMULATE:   # 1 in 6 items is bad
        import random
        return ("defective", 0.93) if random.random() < 1 / 6 else ("good", 0.97)
    # no model yet: a simple colour rule as the BASELINE (beat it with AI later)
    import numpy as np
    roi = frame[frame.shape[0] // 3: 2 * frame.shape[0] // 3]
    return ("defective", 0.9) if np.mean(roi[:, :, 2]) < 80 else ("good", 0.9)


def on_item():
    items.put(time.perf_counter())   # timestamp of the beam break = INPUT time


def worker():
    while True:
        t0 = items.get()
        label, conf = classify(cam.read())
        bad = label in a.bad and conf >= a.min_conf
        stats["total"] += 1
        if bad:
            # wait until the item reaches the pusher, then reject it
            delay = a.travel_s - (time.perf_counter() - t0)
            if delay > 0:
                time.sleep(delay)
            pusher.push()
            stats["rejected"] += 1
        ms = lat.stop(t0, label)               # beam break -> decision/action
        log.write(label=label, conf=round(conf, 3), rejected=bad, latency_ms=round(ms, 1))
        mq.publish(f"{a.topic}/item", {"ts": round(time.time(), 2), "label": label,
                                       "conf": round(conf, 3), "rejected": bad})


threading.Thread(target=worker, daemon=True).start()
object_counter(pin=17, on_object=on_item)
belt.ramp(a.speed, 1.5)
print("belt running - Ctrl+C to stop")
try:
    while True:
        if SIMULATE:
            on_item()                             # fake an item every second
        time.sleep(1 if SIMULATE else 5)
        minutes = (time.time() - stats["start"]) / 60
        mq.publish(f"{a.topic}/status", {
            "ts": round(time.time(), 2), "total": stats["total"], "rejected": stats["rejected"],
            "throughput_per_min": round(stats["total"] / max(minutes, 1e-6), 1),
            "speed": a.speed})
except KeyboardInterrupt:
    belt.ramp(0, 1)
    print("\n", lat.summary(), "| items:", stats)
    mq.close()
