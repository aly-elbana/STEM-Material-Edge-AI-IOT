"""Merge YOLO detection datasets with DIFFERENT class lists (e.g. two Roboflow exports).

Dataset A classes: [person, car, bicycle]     Dataset B classes: [Car, Pedestrian, Dog]
Target classes:    [person, car]
map.json:
{
  "target": ["person", "car"],
  "A": {"person": "person", "car": "car", "bicycle": null},
  "B": {"Car": "car", "Pedestrian": "person", "Dog": null}
}
Each source folder must look like:  A/images/*.jpg  A/labels/*.txt  A/data.yaml (names: [...])
    python -m ml.datasets.merge_yolo_datasets map.json --src A=dsA B=dsB --out merged_yolo
Then split it:  python -m ml.datasets.split_dataset merged_yolo --yolo
Boxes of dropped classes are removed; images left with no boxes are kept as
"background" images (they teach the model what is NOT an object) unless --drop-empty.
"""
import argparse
import json
import os
import shutil

import yaml

p = argparse.ArgumentParser()
p.add_argument("mapping")
p.add_argument("--src", nargs="+", required=True)
p.add_argument("--out", default="merged_yolo")
p.add_argument("--drop-empty", action="store_true")
a = p.parse_args()
m = json.load(open(a.mapping))
target = m["target"]
os.makedirs(f"{a.out}/images", exist_ok=True)
os.makedirs(f"{a.out}/labels", exist_ok=True)
for item in a.src:
    name, root = item.split("=", 1)
    names = yaml.safe_load(open(os.path.join(root, "data.yaml")))["names"]
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names)]
    remap = {}
    for i, n in enumerate(names):
        new = m[name].get(n, None)
        remap[i] = target.index(new) if new is not None else None
    kept = dropped = 0
    for fn in os.listdir(os.path.join(root, "images")):
        stem = os.path.splitext(fn)[0]
        lab = os.path.join(root, "labels", stem + ".txt")
        lines = []
        if os.path.exists(lab):
            for line in open(lab):
                parts = line.split()
                if not parts:
                    continue
                new_id = remap.get(int(parts[0]))
                if new_id is None:
                    dropped += 1
                    continue
                lines.append(" ".join([str(new_id)] + parts[1:]))
        if a.drop_empty and not lines:
            continue
        shutil.copy2(os.path.join(root, "images", fn), f"{a.out}/images/{name}_{fn}")
        open(f"{a.out}/labels/{name}_{stem}.txt", "w").write("\n".join(lines) + ("\n" if lines else ""))
        kept += len(lines)
    print(f"{name}: kept {kept} boxes, dropped {dropped}")
yaml.safe_dump({"path": os.path.abspath(a.out), "train": "images", "val": "images",
                "names": {i: n for i, n in enumerate(target)}},
               open(f"{a.out}/data.yaml", "w"), sort_keys=False)
print("wrote", f"{a.out}/data.yaml")
