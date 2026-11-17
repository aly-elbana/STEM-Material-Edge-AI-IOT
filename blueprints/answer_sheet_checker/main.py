"""Answer-sheet (MCQ) checker with a camera (educational pathway - "homework checker").

1. Print the sheet from make_sheet.py. 2. Student fills bubbles. 3. Camera reads it:
find the 4 ArUco corners -> straighten -> measure how dark each bubble is -> answers ->
compare with the key -> score -> teacher dashboard (MQTT) + class statistics.

    python -m blueprints.answer_sheet_checker.make_sheet
    python -m blueprints.answer_sheet_checker.main --image example_filled.png --key A B C D A B C D A B
    SIMULATE=0 python -m blueprints.answer_sheet_checker.main --camera --key ...
Accuracy evidence: check 50 real sheets by hand and by the machine; report % bubbles read correctly.
"""
import argparse
import json
import time

import cv2
import numpy as np

from blueprints.answer_sheet_checker.make_sheet import H, MARK, MARGIN, W, layout
from common.mqtt_client import EdgeMQTT


def straighten(gray):
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    det = cv2.aruco.ArucoDetector(d, cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(gray)
    if ids is None or len(ids) < 4:
        raise ValueError("need all 4 corner markers in view")
    found = {int(i): c[0] for i, c in zip(ids.flatten(), corners)}
    # outer corner of each marker: TL of 0, TR of 1, BR of 2, BL of 3
    src = np.float32([found[0][0], found[1][1], found[2][2], found[3][3]])
    dst = np.float32([[MARGIN, MARGIN], [W - MARGIN, MARGIN], [W - MARGIN, H - MARGIN], [MARGIN, H - MARGIN]])
    return cv2.warpPerspective(gray, cv2.getPerspectiveTransform(src, dst), (W, H))


def read_answers(page, nq, nc, min_fill=0.45):
    _, th = cv2.threshold(page, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    answers = []
    for row in layout(nq, nc):
        fills = []
        for x, y in row:
            mask = np.zeros_like(th)
            cv2.circle(mask, (x, y), 20, 255, -1)
            fills.append(cv2.countNonZero(cv2.bitwise_and(th, mask)) / cv2.countNonZero(mask))
        best = int(np.argmax(fills))
        second = sorted(fills)[-2] if nc > 1 else 0
        if fills[best] < min_fill:
            answers.append(None)                      # blank
        elif second > min_fill:
            answers.append("multi")                   # two bubbles filled
        else:
            answers.append(best)
    return answers


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image")
    p.add_argument("--camera", action="store_true")
    p.add_argument("--key", nargs="+", required=True, help="e.g. A C B D ...")
    p.add_argument("--student", default="unknown")
    a = p.parse_args()
    key = ["ABCDEF".index(k.upper()) for k in a.key]
    meta = json.load(open("sheet_layout.json")) if not a.camera else {"choices": 4}
    if a.camera:
        from common.camera import Camera
        frame = Camera((1920, 1080)).read()
    else:
        frame = cv2.imread(a.image)
    t0 = time.perf_counter()
    page = straighten(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    got = read_answers(page, len(key), meta["choices"])
    score = sum(g == k for g, k in zip(got, key))
    ms = (time.perf_counter() - t0) * 1000
    pretty = ["-" if g is None else "?" if g == "multi" else "ABCDEF"[g] for g in got]
    print("answers:", " ".join(pretty), f"| score {score}/{len(key)} | {ms:.0f} ms")
    EdgeMQTT("checker1").publish("stem/team00/checker1/result", {
        "ts": round(time.time(), 2), "student": a.student, "answers": pretty,
        "score": score, "out_of": len(key)})
    time.sleep(0.5)
