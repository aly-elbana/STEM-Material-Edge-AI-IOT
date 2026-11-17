"""Split a dataset into train / val / test ONCE, and never touch test until the end.

Image classification (class folders):
    python -m ml.datasets.split_dataset my_images --out split --ratios 0.7 0.15 0.15
    -> split/train/<class>/..., split/val/<class>/..., split/test/<class>/...
YOLO (images/ + labels/):
    python -m ml.datasets.split_dataset merged_yolo --yolo --out yolo_split
    -> yolo_split/{train,val,test}/{images,labels} + data.yaml

--group-prefix N: keep files that share the first N characters of their name together
(e.g. all photos of the same object / same session), so near-duplicates don't leak
from train into test.
"""
import argparse
import os
import random
import shutil
from collections import defaultdict

import yaml

IMG = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def split_list(items, ratios, seed=42):
    random.Random(seed).shuffle(items)
    n = len(items)
    a, b = int(ratios[0] * n), int((ratios[0] + ratios[1]) * n)
    return {"train": items[:a], "val": items[a:b], "test": items[b:]}


def groups_of(files, prefix):
    if not prefix:
        return [[f] for f in files]
    g = defaultdict(list)
    for f in files:
        g[f[:prefix]].append(f)
    return list(g.values())


p = argparse.ArgumentParser()
p.add_argument("src")
p.add_argument("--out", default="split")
p.add_argument("--ratios", nargs=3, type=float, default=[0.7, 0.15, 0.15])
p.add_argument("--yolo", action="store_true")
p.add_argument("--group-prefix", type=int, default=0)
a = p.parse_args()

if a.yolo:
    imgs = sorted(f for f in os.listdir(f"{a.src}/images") if f.lower().endswith(IMG))
    parts = split_list(groups_of(imgs, a.group_prefix), a.ratios)
    for part, groups in parts.items():
        os.makedirs(f"{a.out}/{part}/images", exist_ok=True)
        os.makedirs(f"{a.out}/{part}/labels", exist_ok=True)
        for g in groups:
            for f in g:
                stem = os.path.splitext(f)[0]
                shutil.copy2(f"{a.src}/images/{f}", f"{a.out}/{part}/images/{f}")
                lab = f"{a.src}/labels/{stem}.txt"
                if os.path.exists(lab):
                    shutil.copy2(lab, f"{a.out}/{part}/labels/{stem}.txt")
        print(part, sum(len(g) for g in groups), "images")
    names = yaml.safe_load(open(f"{a.src}/data.yaml"))["names"]
    yaml.safe_dump({"path": os.path.abspath(a.out), "train": "train/images", "val": "val/images",
                    "test": "test/images", "names": names}, open(f"{a.out}/data.yaml", "w"), sort_keys=False)
    print("wrote", f"{a.out}/data.yaml")
else:
    for cls in sorted(os.listdir(a.src)):
        cdir = os.path.join(a.src, cls)
        if not os.path.isdir(cdir):
            continue
        files = sorted(f for f in os.listdir(cdir) if f.lower().endswith(IMG))
        parts = split_list(groups_of(files, a.group_prefix), a.ratios)
        for part, groups in parts.items():
            os.makedirs(f"{a.out}/{part}/{cls}", exist_ok=True)
            for g in groups:
                for f in g:
                    shutil.copy2(os.path.join(cdir, f), f"{a.out}/{part}/{cls}/{f}")
        print(f"{cls:15s} " + "  ".join(f"{k}={sum(len(g) for g in v)}" for k, v in parts.items()))
