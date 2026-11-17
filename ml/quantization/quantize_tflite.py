"""Quantize any Keras model (.keras / SavedModel) to TFLite in 3 flavours.

    python -m ml.quantization.quantize_tflite model.keras --rep-dir split/train --size 224
    python -m ml.quantization.quantize_tflite sensor_model.keras --rep-csv train.csv --features temp vib cur
"""
import argparse
import os

import numpy as np
import tensorflow as tf

p = argparse.ArgumentParser()
p.add_argument("model")
p.add_argument("--rep-dir", help="image folder (class subfolders) for int8 calibration")
p.add_argument("--rep-csv", help="CSV for int8 calibration (sensor models)")
p.add_argument("--features", nargs="*")
p.add_argument("--size", type=int, default=224)
p.add_argument("--out", default="models/quantized")
a = p.parse_args()
os.makedirs(a.out, exist_ok=True)
model = tf.keras.models.load_model(a.model)


def rep():
    if a.rep_csv:
        import pandas as pd
        X = pd.read_csv(a.rep_csv)[a.features].values.astype("float32")
        for row in X[np.random.choice(len(X), min(200, len(X)), replace=False)]:
            yield [row[None]]
    else:
        ds = tf.keras.utils.image_dataset_from_directory(a.rep_dir, image_size=(a.size, a.size),
                                                         batch_size=1, shuffle=True)
        for img, _ in ds.take(150):
            yield [tf.cast(img, tf.float32)]


variants = {
    "fp32": {},
    "fp16": {"opt": True, "fp16": True},
    "dynamic": {"opt": True},
}
if a.rep_dir or a.rep_csv:
    variants["int8"] = {"opt": True, "rep": True}
for name, v in variants.items():
    c = tf.lite.TFLiteConverter.from_keras_model(model)
    if v.get("opt"):
        c.optimizations = [tf.lite.Optimize.DEFAULT]
    if v.get("fp16"):
        c.target_spec.supported_types = [tf.float16]
    if v.get("rep"):
        c.representative_dataset = rep
    path = os.path.join(a.out, f"model_{name}.tflite")
    open(path, "wb").write(c.convert())
    print(f"{name:8s} {os.path.getsize(path) / 1e6:7.3f} MB  -> {path}")
