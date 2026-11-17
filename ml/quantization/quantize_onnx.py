"""Quantize an ONNX model (e.g. exported YOLO or a scikit-learn model via skl2onnx).

    pip install onnx onnxruntime
    python -m ml.quantization.quantize_onnx model.onnx
-> model_int8.onnx (dynamic quantization: weights int8, no calibration data needed)
"""
import argparse
import os

from onnxruntime.quantization import QuantType, quantize_dynamic

p = argparse.ArgumentParser()
p.add_argument("model")
a = p.parse_args()
out = a.model.replace(".onnx", "_int8.onnx")
quantize_dynamic(a.model, out, weight_type=QuantType.QInt8)
print(f"{os.path.getsize(a.model) / 1e6:.2f} MB -> {os.path.getsize(out) / 1e6:.2f} MB  ({out})")
