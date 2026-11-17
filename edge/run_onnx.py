"""Run an .onnx model with onnxruntime and time it.

    python -m edge.run_onnx model.onnx --input 36.2 0.91 4.8 --bench
"""
import argparse

import numpy as np
import onnxruntime as ort

from common.timing import benchmark

p = argparse.ArgumentParser()
p.add_argument("model")
p.add_argument("--input", type=float, nargs="*")
p.add_argument("--bench", action="store_true")
a = p.parse_args()
sess = ort.InferenceSession(a.model, providers=["CPUExecutionProvider"])
i = sess.get_inputs()[0]
shape = [d if isinstance(d, int) else 1 for d in i.shape]
x = np.array([a.input], np.float32) if a.input else np.random.rand(*shape).astype(np.float32)
print("input", i.name, shape, "->", [o.shape for o in sess.run(None, {i.name: x})])
if a.bench:
    print(benchmark(lambda: sess.run(None, {i.name: x}), runs=100))
