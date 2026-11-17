"""One camera class for every project.

    cam = Camera(size=(640, 480))
    frame = cam.read()        # numpy array, BGR (OpenCV order), shape (H, W, 3)

Order of attempts:
  1. Raspberry Pi camera via Picamera2 (CSI ribbon: Camera Module 3, AI Camera...)
  2. USB webcam via OpenCV (index 0) - also works on a laptop
  3. SIMULATE: synthetic frames (moving shapes) so code runs anywhere
"""
import time

import numpy as np

from common import SIMULATE


class Camera:
    def __init__(self, size=(640, 480), index=0):
        self.size = size
        self.kind = None
        if not SIMULATE:
            try:
                from picamera2 import Picamera2
                self.picam = Picamera2()
                # "RGB888" in Picamera2 gives pixels in BGR order = what OpenCV expects
                cfg = self.picam.create_preview_configuration(
                    main={"format": "RGB888", "size": size})
                self.picam.configure(cfg)
                self.picam.start()
                time.sleep(1.0)  # let exposure settle
                self.kind = "picamera2"
            except Exception as e:
                print("[camera] Picamera2 not available:", e)
            if self.kind is None:
                import cv2
                self.cap = cv2.VideoCapture(index)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
                if self.cap.isOpened():
                    self.kind = "opencv"
        if self.kind is None:
            self.kind = "synthetic"
            self._t = 0
        print(f"[camera] using {self.kind}")

    def read(self):
        if self.kind == "picamera2":
            return self.picam.capture_array()
        if self.kind == "opencv":
            ok, frame = self.cap.read()
            if not ok:
                raise RuntimeError("camera read failed")
            return frame
        # synthetic: grey belt with a box moving left -> right
        w, h = self.size
        frame = np.full((h, w, 3), 90, np.uint8)
        x = (self._t * 15) % (w + 120) - 120
        frame[h // 3: h // 3 + 120, max(0, x): max(0, x + 120)] = (40, 160, 230)
        self._t += 1
        return frame

    def close(self):
        if self.kind == "picamera2":
            self.picam.stop()
        elif self.kind == "opencv":
            self.cap.release()
