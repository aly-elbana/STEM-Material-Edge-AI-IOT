"""Lab C: run the model ON the device and time it.  pip install ai-edge-litert
LiteRT is the new name of TensorFlow Lite.
"""
import time, numpy as np
from ai_edge_litert.interpreter import Interpreter

CLASSES = ["bearing", "normal", "overheat", "overload"]

it = Interpreter(model_path="m3_model.tflite")
it.allocate_tensors()
inp = it.get_input_details()[0]
out = it.get_output_details()[0]

for reading in ([32.1, 0.61, 4.2], [32.3, 0.98, 4.3], [37.0, 0.60, 4.2]):
    x = np.array([reading], dtype=np.float32)
    t0 = time.perf_counter()
    it.set_tensor(inp["index"], x); it.invoke()
    score = it.get_tensor(out["index"])[0]
    ms = (time.perf_counter() - t0) * 1000
    print(reading, "->", CLASSES[int(score.argmax())],
          f"({score.max():.0%})", f"{ms:.2f} ms")
