"""Blink detection + face distance from the camera with MediaPipe Face Landmarker
(Tasks API - the old mp.solutions API is no longer shipped in new mediapipe versions).

    pip install mediapipe
    wget -O face_landmarker.task \
      https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

EAR (Eye Aspect Ratio) = eye height / eye width. Open eye ~0.25-0.35, closed < ~0.2.
A blink = EAR below the threshold for >= 2 frames, then back up.
Calibrate THRESHOLD for each person with calibrate() - this is your AI evidence:
label 200 frames open/closed, measure accuracy of the detector (>= 80 %).
"""
import math
import time

import numpy as np

RIGHT = [33, 160, 158, 133, 153, 144]     # p1..p6 around the right eye
LEFT = [362, 385, 387, 263, 373, 380]
CHEEK_L, CHEEK_R = 234, 454               # face edges -> face width in pixels


def ear(lm, idx, w, h):
    """Eye Aspect Ratio in pixel units (so the image aspect ratio does not distort it)."""
    p = [(lm[i].x * w, lm[i].y * h) for i in idx]
    return (math.dist(p[1], p[5]) + math.dist(p[2], p[4])) / (2.0 * math.dist(p[0], p[3]) + 1e-9)


class BlinkMeter:
    def __init__(self, model_path="face_landmarker.task", threshold=0.21, min_frames=2):
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
        self.mp = mp
        opts = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO, num_faces=1,
            output_face_blendshapes=True)
        self.lm = vision.FaceLandmarker.create_from_options(opts)
        self.threshold, self.min_frames = threshold, min_frames
        self.closed_frames, self.blinks, self.t0 = 0, [], time.time()
        self.focal_px = None   # set by calibrate_distance()

    def update(self, bgr):
        """Returns dict(face, ear, blink_now, blinks_per_min, face_width_px, distance_cm)."""
        rgb = np.ascontiguousarray(bgr[:, :, ::-1])
        h, w = rgb.shape[:2]
        img = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb)
        res = self.lm.detect_for_video(img, int(time.time() * 1000))
        if not res.face_landmarks:
            return {"face": False}
        lm = res.face_landmarks[0]
        e = (ear(lm, LEFT, w, h) + ear(lm, RIGHT, w, h)) / 2
        blink = False
        if e < self.threshold:
            self.closed_frames += 1
        else:
            if self.closed_frames >= self.min_frames:
                blink = True
                self.blinks.append(time.time())
            self.closed_frames = 0
        now = time.time()
        self.blinks = [b for b in self.blinks if now - b < 60]
        minutes = min(1.0, (now - self.t0) / 60)
        face_w = abs(lm[CHEEK_L].x - lm[CHEEK_R].x) * w
        dist = self.focal_px * 14.0 / face_w if self.focal_px and face_w > 0 else None
        return {"face": True, "ear": round(e, 3), "blink_now": blink,
                "blinks_per_min": round(len(self.blinks) / max(minutes, 1 / 60), 1),
                "face_width_px": round(face_w, 1), "distance_cm": round(dist, 1) if dist else None}

    def calibrate_distance(self, face_width_px, known_distance_cm, face_width_cm=14.0):
        """Sit at a measured distance (e.g. 50 cm), read face_width_px, call this once.
        Pinhole model: distance = focal * real_width / pixel_width."""
        self.focal_px = face_width_px * known_distance_cm / face_width_cm
