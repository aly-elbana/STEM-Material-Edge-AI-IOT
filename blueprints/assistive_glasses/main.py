"""Assistive glasses / cane for visually impaired people (medical pathway example).

Camera + YOLO (what is ahead) + distance sensor (how far) -> voice + vibration.
Only speaks about the NEAREST important object, with a cooldown, so it does not talk all the time.

    python -m blueprints.assistive_glasses.main                          # simulation
    SIMULATE=0 python -m blueprints.assistive_glasses.main --model yolo26n_ncnn_model --tof --lang ar
Speed tips: --imgsz 320, NCNN export, or the AI Camera / AI HAT+ for real-time.
"""
import argparse
import random
import time

from common import SIMULATE
from common.alerts import say
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog
from motors.switching import PWMLoad
from sensors import hcsr04, vl53l0x

IMPORTANT = {"person": "شخص", "car": "عربية", "bicycle": "عجلة", "motorcycle": "موتوسيكل",
             "bus": "أتوبيس", "truck": "نقل", "dog": "كلب", "chair": "كرسي", "bench": "دكة",
             "stop sign": "علامة قف", "traffic light": "إشارة"}

p = argparse.ArgumentParser()
p.add_argument("--model", default="yolo26n.pt")
p.add_argument("--imgsz", type=int, default=320)
p.add_argument("--tof", action="store_true", help="VL53L0X (up to ~2 m) instead of HC-SR04")
p.add_argument("--warn-m", type=float, default=1.5)
p.add_argument("--lang", default="en")
p.add_argument("--topic", default="stem/team00/glasses1/status")
a = p.parse_args()

vib = PWMLoad(pin=13)            # coin vibration motor through a transistor/MOSFET
mq, lat = EdgeMQTT("glasses1"), LatencyLog("glasses_latency.csv")
model = cam = None
if not SIMULATE:
    from ultralytics import YOLO
    from common.camera import Camera
    model, cam = YOLO(a.model, task="detect"), Camera((640, 480))
last_spoken = {}

while True:
    t0 = lat.start()
    dist_m = (vl53l0x.read_cm() if a.tof else hcsr04.read_cm()) / 100
    if SIMULATE:
        objs = [(random.choice(list(IMPORTANT)), random.uniform(0.4, 0.9), random.uniform(0.2, 0.8))]
    else:
        r = model.predict(cam.read(), imgsz=a.imgsz, conf=0.45, verbose=False)[0]
        objs = []
        for b in r.boxes:
            name = r.names[int(b.cls)]
            if name in IMPORTANT:
                x1, y1, x2, y2 = b.xyxyn[0].tolist()
                objs.append((name, float(b.conf), (x2 - x1) * (y2 - y1)))   # bigger box ~ closer
    vib.set(1.0 if dist_m < 0.7 else 0.5 if dist_m < a.warn_m else 0.0)  # haptic = instant
    if objs and dist_m < a.warn_m:
        name = max(objs, key=lambda o: o[2])[0]
        if time.time() - last_spoken.get(name, 0) > 4:
            last_spoken[name] = time.time()
            if a.lang == "ar":
                say(f"{IMPORTANT[name]} قدامك على بعد {dist_m:.1f} متر", "ar")
            else:
                say(f"{name} ahead, {dist_m:.1f} meters", "en")
    ms = lat.stop(t0, ",".join(o[0] for o in objs))
    mq.publish(a.topic, {"ts": round(time.time(), 2), "distance_m": round(dist_m, 2),
                         "objects": [o[0] for o in objs], "loop_ms": round(ms, 1)})
    if SIMULATE:
        time.sleep(1)
