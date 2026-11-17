"""Smart classroom (educational pathway) - continues Part 1's lab.

Occupancy from PIR + camera person count (YOLO class 0), comfort from BME280,
air from SGP30 (or SCD41 for true CO2), light from LTR390.
Acts: lights relay (occupied + dark), fan relay (hot or stale air), alerts to the teacher.
The AI part: "occupied?" must be right even when students sit STILL (PIR alone fails there).
    python -m blueprints.smart_classroom.main
    SIMULATE=0 python -m blueprints.smart_classroom.main --camera --model yolo26n_ncnn_model
"""
import argparse
import random
import time

from common import SIMULATE
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from motors.switching import Switch
from sensors import bme280, ltr390_uv, sgp30_air

p = argparse.ArgumentParser()
p.add_argument("--camera", action="store_true")
p.add_argument("--model", default="yolo26n.pt")
p.add_argument("--min-lux", type=float, default=300)
p.add_argument("--max-temp", type=float, default=28)
p.add_argument("--max-eco2", type=float, default=1000)
p.add_argument("--topic", default="stem/team00/class1/status")
a = p.parse_args()

lights, fan = Switch(26, name="lights"), Switch(19, name="fan")
mq = EdgeMQTT("class1")
log = CSVLogger("data/classroom.csv", ["pir", "people", "occupied", "temp_c", "humidity",
                                       "eco2_ppm", "lux", "lights", "fan"])
pir = model = cam = None
if not SIMULATE:
    from sensors.digital_inputs import motion
    pir = motion(17)
    if a.camera:
        from ultralytics import YOLO
        from common.camera import Camera
        model, cam = YOLO(a.model, task="detect"), Camera((640, 480))
last_motion = 0
while True:
    moving = (random.random() < 0.3) if SIMULATE else pir.motion_detected
    last_motion = time.time() if moving else last_motion
    people = 0
    if model:
        r = model.predict(cam.read(), imgsz=320, conf=0.4, classes=[0], verbose=False)[0]
        people = len(r.boxes)
    elif SIMULATE:
        people = random.choice([0, 0, 3, 12, 25])
    occupied = people > 0 or time.time() - last_motion < 120   # fuse camera + PIR
    env, air, light = bme280.read(), sgp30_air.read(), ltr390_uv.read()
    want_lights = occupied and light["lux"] < a.min_lux
    want_fan = occupied and (env["temp_c"] > a.max_temp or air["eco2_ppm"] > a.max_eco2)
    (lights.on if want_lights else lights.off)()
    (fan.on if want_fan else fan.off)()
    row = {"pir": int(moving), "people": people, "occupied": int(occupied), "temp_c": env["temp_c"],
           "humidity": env["humidity"], "eco2_ppm": air["eco2_ppm"], "lux": light["lux"],
           "lights": int(want_lights), "fan": int(want_fan)}
    log.write(**row)
    mq.publish(a.topic, {"ts": round(time.time(), 2), **row})
    time.sleep(2)
