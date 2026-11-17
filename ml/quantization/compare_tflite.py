"""Compare .tflite models: size, speed, accuracy on the TEST images.

    python -m ml.quantization.compare_tflite models/image split/test
"""
import argparse
import glob
import os

import cv2
import numpy as np

from common.timing import benchmark
from ml.image.classify_live import TFLiteClassifier

p = argparse.ArgumentParser()
p.add_argument("model_dir")
p.add_argument("test_dir")
a = p.parse_args()
labels = os.path.join(a.model_dir, "labels.txt")
samples = []
for cls in sorted(os.listdir(a.test_dir)):
    for f in glob.glob(os.path.join(a.test_dir, cls, "*")):
        samples.append((f, cls))
print(f"{'model':28s} {'MB':>6s} {'ms':>7s} {'acc':>6s}")
for path in sorted(glob.glob(os.path.join(a.model_dir, "*.tflite"))):
    clf = TFLiteClassifier(path, labels)
    correct = 0
    for f, cls in samples:
        pred, _, _ = clf.predict(cv2.imread(f))
        correct += pred == cls
    img = cv2.imread(samples[0][0])
    t = benchmark(lambda: clf.predict(img), runs=30)
    print(f"{os.path.basename(path):28s} {os.path.getsize(path) / 1e6:6.2f} {t['mean_ms']:7.1f} "
          f"{correct / max(len(samples), 1):6.1%}")
