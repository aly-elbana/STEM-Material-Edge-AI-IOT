"""Run ANY .tflite model (sensor model or image model) and time it.

    python -m edge.run_tflite model.tflite --input 36.2 0.91 4.8
    python -m edge.run_tflite model.tflite --bench           # random input, 100 runs
"""
import argparse

import numpy as np

from common.timing import benchmark


def load(path, threads=4):
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        from tflite_runtime.interpreter import Interpreter
    it = Interpreter(model_path=path, num_threads=threads)
    it.allocate_tensors()
    return it


def run(it, x):
    inp, out = it.get_input_details()[0], it.get_output_details()[0]
    it.set_tensor(inp["index"], x.astype(inp["dtype"]))
    it.invoke()
    return it.get_tensor(out["index"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--input", type=float, nargs="*")
    p.add_argument("--bench", action="store_true")
    a = p.parse_args()
    it = load(a.model)
    d = it.get_input_details()[0]
    print("input:", d["shape"], d["dtype"].__name__, "| output:", it.get_output_details()[0]["shape"])
    x = np.array([a.input], np.float32) if a.input else np.random.rand(*d["shape"]).astype(np.float32)
    print("output:", run(it, x))
    if a.bench:
        print(benchmark(lambda: run(it, x), runs=100))
