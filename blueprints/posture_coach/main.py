"""Posture coach for students at a desk (health pathway, camera only, no wearables).

MediaPipe Pose Landmarker (Tasks API) -> ear, shoulder, hip points -> neck angle.
Slouching (head forward) for more than 30 s -> gentle reminder.
    pip install mediapipe
    wget -O pose_landmarker_lite.task \
      https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task
    SIMULATE=0 python -m blueprints.posture_coach.main
AI evidence: label 300 frames good/slouched (several students, with consent), compare the
angle rule vs a classifier on landmark features (ml.tabular), report accuracy on test frames.
"""
import math
import random
import time

import numpy as np

from common import SIMULATE
from common.alerts import say
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT

EAR, SHOULDER, HIP = 7, 11, 23           # left side landmarks (use 8, 12, 24 for the right side)
LIMIT_DEG, HOLD_S = 25, 30


def neck_angle(lm):
    ex, ey = lm[EAR].x, lm[EAR].y
    sx, sy = lm[SHOULDER].x, lm[SHOULDER].y
    return abs(math.degrees(math.atan2(ex - sx, sy - ey)))   # 0 = ear straight above shoulder


mq, log = EdgeMQTT("posture1"), CSVLogger("data/posture.csv", ["neck_deg", "slouch"])
if not SIMULATE:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    from common.camera import Camera
    cam = Camera((640, 480))
    det = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path="pose_landmarker_lite.task"),
        running_mode=vision.RunningMode.VIDEO))
bad_since = None
while True:
    if SIMULATE:
        ang = abs(random.gauss(18, 10))
    else:
        rgb = np.ascontiguousarray(cam.read()[:, :, ::-1])
        res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                                   int(time.time() * 1000))
        if not res.pose_landmarks:
            continue
        ang = neck_angle(res.pose_landmarks[0])
    slouch = ang > LIMIT_DEG
    bad_since = (bad_since or time.time()) if slouch else None
    if bad_since and time.time() - bad_since > (3 if SIMULATE else HOLD_S):
        say("Sit up straight, please")
        bad_since = None
    log.write(neck_deg=round(ang, 1), slouch=int(slouch))
    mq.publish("stem/team00/posture1/status", {"ts": round(time.time(), 2), "neck_deg": round(ang, 1),
                                               "slouch": slouch})
    time.sleep(0.5 if SIMULATE else 0.1)
