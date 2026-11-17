"""Multiply a SMALL image dataset with realistic variations (only the TRAIN split!).
Never augment the test set - it must stay like the real world.

    python -m ml.datasets.augment_images split/train --per-image 4

Variations: rotation, flip, brightness, contrast, blur, noise, small crop/zoom.
Choose ones that can really happen in your project (a bottle on a belt can be
brighter/darker or slightly rotated; it will not be upside down).
For YOLO you don't need this: Ultralytics augments during training automatically.
"""
import argparse
import os
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

p = argparse.ArgumentParser()
p.add_argument("folder", help="folder with class subfolders")
p.add_argument("--per-image", type=int, default=3)
p.add_argument("--no-flip", action="store_true")
a = p.parse_args()


def vary(im):
    if not a.no_flip and random.random() < 0.5:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.rotate(random.uniform(-15, 15), expand=False, fillcolor=(128, 128, 128))
    im = ImageEnhance.Brightness(im).enhance(random.uniform(0.7, 1.3))
    im = ImageEnhance.Contrast(im).enhance(random.uniform(0.8, 1.2))
    if random.random() < 0.3:
        im = im.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 1.2)))
    w, h = im.size
    s = random.uniform(0.85, 1.0)
    x, y = random.randint(0, int(w * (1 - s))), random.randint(0, int(h * (1 - s)))
    im = im.crop((x, y, x + int(w * s), y + int(h * s))).resize((w, h))
    if random.random() < 0.3:
        arr = np.asarray(im).astype(np.int16) + np.random.normal(0, 6, (h, w, 3)).astype(np.int16)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return im


made = 0
for cls in os.listdir(a.folder):
    cdir = os.path.join(a.folder, cls)
    if not os.path.isdir(cdir):
        continue
    for fn in [f for f in os.listdir(cdir) if not f.startswith("aug_")]:
        try:
            im = Image.open(os.path.join(cdir, fn)).convert("RGB")
        except Exception:
            continue
        for k in range(a.per_image):
            vary(im).save(os.path.join(cdir, f"aug_{k}_{os.path.splitext(fn)[0]}.jpg"), quality=92)
            made += 1
print("created", made, "augmented images")
