"""Export a YOLO model for the edge device.

    python -m ml.yolo.export best.pt --format ncnn              # Pi 5 CPU (recommended)
    python -m ml.yolo.export best.pt --format onnx
    python -m ml.yolo.export best.pt --format tflite --int8 --data data.yaml
    python -m ml.yolo.export best.pt --format imx --data data.yaml   # Raspberry Pi AI Camera
--imgsz 320 makes it ~3-4x faster (smaller objects get harder to see).
INT8 needs --data so it can calibrate on real images; always re-check accuracy after.
"""
import argparse

from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("weights")
p.add_argument("--format", default="ncnn", choices=["ncnn", "onnx", "tflite", "openvino", "imx", "torchscript"])
p.add_argument("--imgsz", type=int, default=640)
p.add_argument("--int8", action="store_true")
p.add_argument("--half", action="store_true", help="FP16")
p.add_argument("--data", help="dataset yaml for INT8 calibration")
a = p.parse_args()
kw = dict(format=a.format, imgsz=a.imgsz)
if a.int8:
    kw["int8"] = True
    if a.data:
        kw["data"] = a.data
if a.half:
    kw["half"] = True
if a.format == "imx" and a.data:
    kw["data"] = a.data
path = YOLO(a.weights).export(**kw)
print("exported ->", path)
