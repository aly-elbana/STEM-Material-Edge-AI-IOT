"""Optional: convert a scikit-learn model to ONNX (runs with onnxruntime, no sklearn
needed on the device). joblib + scikit-learn on the Pi is usually simpler and fine.

    pip install skl2onnx onnxruntime
    python -m ml.quantization.sklearn_to_onnx models
"""
import argparse
import json
import os

import joblib
from skl2onnx import to_onnx
import numpy as np

p = argparse.ArgumentParser()
p.add_argument("folder")
a = p.parse_args()
model = joblib.load(os.path.join(a.folder, "model.joblib"))
feats = json.load(open(os.path.join(a.folder, "features.json")))["features"]
onx = to_onnx(model, np.zeros((1, len(feats)), dtype=np.float32), target_opset=17)
open(os.path.join(a.folder, "model.onnx"), "wb").write(onx.SerializeToString())
print("saved", os.path.join(a.folder, "model.onnx"))
