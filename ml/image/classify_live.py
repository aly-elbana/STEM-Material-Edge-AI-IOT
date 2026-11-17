"""Run an image classifier (.tflite) on the Pi camera, live, with timing.

    python -m ml.image.classify_live --model models/image/model_fp16.tflite \
        --labels models/image/labels.txt
Also works with a Teachable Machine export (Image -> Tensorflow Lite -> Floating point):
    --model model_unquant.tflite --labels labels.txt --tm
"""
import argparse
import time

import cv2
import numpy as np

from common.camera import Camera


class TFLiteClassifier:
    def __init__(self, model_path, labels_path, teachable_machine=False):
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            from tflite_runtime.interpreter import Interpreter
        self.it = Interpreter(model_path=model_path, num_threads=4)
        self.it.allocate_tensors()
        self.inp = self.it.get_input_details()[0]
        self.out = self.it.get_output_details()[0]
        self.h, self.w = self.inp["shape"][1:3]
        self.labels = [l.strip().split(" ", 1)[-1] if teachable_machine else l.strip()
                       for l in open(labels_path) if l.strip()]
        self.tm = teachable_machine

    def predict(self, bgr):
        rgb = cv2.cvtColor(cv2.resize(bgr, (self.w, self.h)), cv2.COLOR_BGR2RGB)
        x = rgb[None].astype(np.float32)
        if self.tm:
            x = x / 127.5 - 1.0           # Teachable Machine expects -1..1
        if self.inp["dtype"] == np.uint8:  # fully-int8 model
            x = rgb[None].astype(np.uint8)
        elif self.inp["dtype"] == np.int8:
            scale, zero = self.inp["quantization"]
            x = np.clip(np.round(x / scale + zero), -128, 127).astype(np.int8)
        t0 = time.perf_counter()
        self.it.set_tensor(self.inp["index"], x)
        self.it.invoke()
        y = self.it.get_tensor(self.out["index"])[0].astype(np.float32)
        if self.out["dtype"] in (np.uint8, np.int8):
            scale, zero = self.out["quantization"]
            y = (y - zero) * scale
        ms = (time.perf_counter() - t0) * 1000
        i = int(np.argmax(y))
        return self.labels[i], float(y[i]), ms


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--tm", action="store_true", help="Teachable Machine model")
    a = p.parse_args()
    clf = TFLiteClassifier(a.model, a.labels, a.tm)
    cam = Camera()
    while True:
        label, conf, ms = clf.predict(cam.read())
        print(f"{label:15s} {conf:5.0%}  {ms:5.1f} ms")
