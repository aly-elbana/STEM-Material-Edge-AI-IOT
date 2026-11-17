"""Merge image datasets whose LABELS DON'T MATCH into one clean dataset.

Example: dataset A has folders  good/  scratched/  dented/
         dataset B has folders  OK/    defect/     dirty/
You want 2 classes: good, defective.  Write a mapping file map.json:
{
  "A": {"good": "good", "scratched": "defective", "dented": "defective"},
  "B": {"OK": "good", "defect": "defective", "dirty": null}
}
null = drop that class. Then:
    python -m ml.datasets.merge_class_folders map.json --src A=path/to/A B=path/to/B --out merged

Result: merged/good/A_xxx.jpg, merged/defective/B_yyy.jpg ...
The source name is kept in the file name, so you can later check
"does my model only work on images from dataset A?" (domain shift).
"""
import argparse
import json
import os
import shutil
from collections import Counter

IMG = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

p = argparse.ArgumentParser()
p.add_argument("mapping")
p.add_argument("--src", nargs="+", required=True, help="NAME=folder")
p.add_argument("--out", default="merged")
a = p.parse_args()
mapping = json.load(open(a.mapping))
counts = Counter()
for item in a.src:
    name, root = item.split("=", 1)
    for cls in sorted(os.listdir(root)):
        cdir = os.path.join(root, cls)
        if not os.path.isdir(cdir):
            continue
        if cls not in mapping.get(name, {}):
            print(f"WARNING: {name}/{cls} not in mapping -> skipped (add it to map.json)")
            continue
        new = mapping[name][cls]
        if new is None:
            continue
        os.makedirs(os.path.join(a.out, new), exist_ok=True)
        for fn in os.listdir(cdir):
            if fn.lower().endswith(IMG):
                shutil.copy2(os.path.join(cdir, fn), os.path.join(a.out, new, f"{name}_{cls}_{fn}"))
                counts[(new, name)] += 1
print("\nimages per (new class, source):")
for (c, s), n in sorted(counts.items()):
    print(f"  {c:15s} from {s:6s}: {n}")
