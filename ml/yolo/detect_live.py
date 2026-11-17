"""Live YOLO detection on the Pi camera with FPS and latency.

    python -m ml.yolo.detect_live --model yolo26n_ncnn_model --imgsz 320 --conf 0.5
    python -m ml.yolo.detect_live --model yolo26n.pt --show        # window (with a screen)
--classes 0 2  -> only person (0) and car (2) for COCO models.
"""
import argparse
import time

from ultralytics import YOLO

from common.camera import Camera

p = argparse.ArgumentParser()
p.add_argument("--model", default="yolo26n.pt")
p.add_argument("--imgsz", type=int, default=320)
p.add_argument("--conf", type=float, default=0.5)
p.add_argument("--classes", type=int, nargs="*")
p.add_argument("--show", action="store_true")
a = p.parse_args()

model = YOLO(a.model, task="detect")
cam = Camera((640, 480))
n, t_start = 0, time.perf_counter()
while True:
    frame = cam.read()
    t0 = time.perf_counter()
    r = model.predict(frame, imgsz=a.imgsz, conf=a.conf, classes=a.classes, verbose=False)[0]
    ms = (time.perf_counter() - t0) * 1000
    found = [(r.names[int(b.cls)], float(b.conf)) for b in r.boxes]
    n += 1
    fps = n / (time.perf_counter() - t_start)
    print(f"{ms:6.1f} ms  {fps:4.1f} FPS  ", ", ".join(f"{c} {p:.0%}" for c, p in found))
    if a.show:
        import cv2
        cv2.imshow("yolo", r.plot())
        if cv2.waitKey(1) == 27:
            break
