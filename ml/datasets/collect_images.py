"""Collect your OWN labelled photos on the Pi, in the real conditions of your project.

    python -m ml.datasets.collect_images --label good --count 200 --every 0.5
    python -m ml.datasets.collect_images --label cap_missing --count 200

Tips: change position, angle, light, background a little between shots.
Collect in the SAME place/light as the exhibition day (or both).
"""
import argparse
import os
import time

import cv2

from common.camera import Camera

p = argparse.ArgumentParser()
p.add_argument("--label", required=True)
p.add_argument("--count", type=int, default=100)
p.add_argument("--every", type=float, default=0.5, help="seconds between photos")
p.add_argument("--out", default="dataset_raw")
p.add_argument("--size", type=int, nargs=2, default=[640, 480])
a = p.parse_args()
folder = os.path.join(a.out, a.label)
os.makedirs(folder, exist_ok=True)
cam = Camera(tuple(a.size))
session = time.strftime("%Y%m%d_%H%M%S")
for i in range(a.count):
    frame = cam.read()
    cv2.imwrite(os.path.join(folder, f"{session}_{i:04d}.jpg"), frame)
    print(f"\r{a.label}: {i + 1}/{a.count}", end="")
    time.sleep(a.every)
cam.close()
print("\nsaved to", folder)
