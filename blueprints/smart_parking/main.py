"""Smart parking / spot occupancy with one camera + YOLO (also: free seats in a library,
shelves on a shop/factory rack). For counting things that MOVE across a line use
ml/yolo/count_line.py instead.

1. Take a photo, open it in any image viewer, note each spot's polygon corners in pixels.
2. spots.json: {"A1": [[100,300],[220,300],[220,420],[100,420]], "A2": [...]}
3. SIMULATE=0 python -m blueprints.smart_parking.main --model yolo26n_ncnn_model --spots spots.json
A spot is occupied if the centre of a car/truck/bus/motorcycle box is inside its polygon.
Use a toy-car model on a printed parking map for the exhibition!
"""
import argparse
import json
import random
import time

import cv2
import numpy as np

from common import SIMULATE
from common.mqtt_client import EdgeMQTT

VEHICLES = {"car", "truck", "bus", "motorcycle"}
p = argparse.ArgumentParser()
p.add_argument("--model", default="yolo26n.pt")
p.add_argument("--spots", default="spots.json")
a = p.parse_args()
spots = (json.load(open(a.spots)) if not SIMULATE else
         {f"A{i}": [[i * 100, 300], [i * 100 + 90, 300], [i * 100 + 90, 420], [i * 100, 420]] for i in range(1, 6)})
mq = EdgeMQTT("parking1")
if not SIMULATE:
    from ultralytics import YOLO
    from common.camera import Camera
    model, cam = YOLO(a.model, task="detect"), Camera((1280, 720))
while True:
    if SIMULATE:
        centers = [(random.randint(100, 590), 360) for _ in range(random.randint(0, 5))]
    else:
        r = model.predict(cam.read(), imgsz=640, conf=0.4, verbose=False)[0]
        centers = [tuple(map(int, b.xywh[0][:2].tolist())) for b in r.boxes if r.names[int(b.cls)] in VEHICLES]
    status = {}
    for name, poly in spots.items():
        pts = np.array(poly, np.int32)
        status[name] = any(cv2.pointPolygonTest(pts, c, False) >= 0 for c in centers)
    free = [k for k, v in status.items() if not v]
    print("free:", free)
    mq.publish("stem/team00/parking1/status", {"ts": round(time.time(), 2), "free": free,
                                               "free_count": len(free), "total": len(spots)})
    time.sleep(2)
