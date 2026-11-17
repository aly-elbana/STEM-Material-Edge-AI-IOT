"""Check a dataset BEFORE training: counts per class, imbalance, tiny/corrupt images,
duplicates. Works for class-folder image datasets and for CSV files.

    python -m ml.datasets.dataset_report my_images
    python -m ml.datasets.dataset_report data.csv --target label
"""
import argparse
import hashlib
import os
from collections import Counter

p = argparse.ArgumentParser()
p.add_argument("path")
p.add_argument("--target", default="label")
a = p.parse_args()

if a.path.endswith(".csv"):
    import pandas as pd
    df = pd.read_csv(a.path)
    print(df.describe(include="all").T.to_string())
    print("\nmissing values per column:\n", df.isna().sum().to_string())
    if a.target in df:
        vc = df[a.target].value_counts()
        print("\nclass counts:\n", vc.to_string())
        print(f"\nimbalance ratio (biggest/smallest): {vc.max() / max(vc.min(), 1):.1f}"
              "  -> above ~5: use class_weight='balanced', collect more of the rare class")
    print("duplicate rows:", int(df.duplicated().sum()))
else:
    from PIL import Image
    counts, sizes, hashes, bad = Counter(), Counter(), Counter(), []
    for cls in sorted(os.listdir(a.path)):
        cdir = os.path.join(a.path, cls)
        if not os.path.isdir(cdir):
            continue
        for fn in os.listdir(cdir):
            fp = os.path.join(cdir, fn)
            try:
                with Image.open(fp) as im:
                    sizes[im.size] += 1
                counts[cls] += 1
                hashes[hashlib.md5(open(fp, "rb").read()).hexdigest()] += 1
            except Exception:
                bad.append(fp)
    for c, n in counts.most_common():
        print(f"{c:20s} {n}")
    if counts:
        print(f"imbalance ratio: {max(counts.values()) / max(min(counts.values()), 1):.1f}")
    print("most common image sizes:", sizes.most_common(3))
    print("exact duplicate files:", sum(v - 1 for v in hashes.values() if v > 1))
    print("unreadable files:", len(bad), bad[:5])
