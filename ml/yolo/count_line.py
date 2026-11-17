"""Count objects crossing a line (conveyor items, people at a door, cars at a gate)
with YOLO tracking (each object keeps its ID between frames, so it is counted once).

    python -m ml.yolo.count_line --model best_ncnn_model --line 0.5 --axis x
--axis x : vertical line at 50 % of the width, objects move left->right (conveyor)
--axis y : horizontal line, objects move up/down (door, gate)
Publishes the count over MQTT every 5 s if --topic is given.
"""
import argparse
import time

from ultralytics import YOLO

from common.camera import Camera

p = argparse.ArgumentParser()
p.add_argument("--model", default="yolo26n.pt")
p.add_argument("--line", type=float, default=0.5)
p.add_argument("--axis", choices=["x", "y"], default="x")
p.add_argument("--imgsz", type=int, default=320)
p.add_argument("--conf", type=float, default=0.4)
p.add_argument("--classes", type=int, nargs="*")
p.add_argument("--topic")
a = p.parse_args()

model = YOLO(a.model, task="detect")
cam = Camera((640, 480))
mq = None
if a.topic:
    from common.mqtt_client import EdgeMQTT
    mq = EdgeMQTT("counter")
last_pos, counted, totals = {}, set(), {}
t_pub, t_start = time.time(), time.time()
while True:
    frame = cam.read()
    h, w = frame.shape[:2]
    limit = a.line * (w if a.axis == "x" else h)
    r = model.track(frame, persist=True, imgsz=a.imgsz, conf=a.conf, classes=a.classes,
                    tracker="bytetrack.yaml", verbose=False)[0]
    if r.boxes.id is not None:
        for box, tid, cls in zip(r.boxes.xywh.tolist(), r.boxes.id.int().tolist(), r.boxes.cls.int().tolist()):
            pos = box[0] if a.axis == "x" else box[1]
            prev = last_pos.get(tid)
            if prev is not None and tid not in counted and (prev - limit) * (pos - limit) < 0:
                counted.add(tid)
                name = r.names[cls]
                totals[name] = totals.get(name, 0) + 1
                print("crossed:", name, "totals:", totals)
            last_pos[tid] = pos
    if mq and time.time() - t_pub > 5:
        minutes = (time.time() - t_start) / 60
        mq.publish(a.topic, {"totals": totals,
                             "per_min": round(sum(totals.values()) / max(minutes, 1e-6), 1)})
        t_pub = time.time()
