"""Create a printable answer sheet with 4 ArUco markers (corners) so the camera can
find and straighten the page automatically, plus a filled example for testing.

    python -m blueprints.answer_sheet_checker.make_sheet --questions 10 --choices 4
-> sheet.png (print it A4), example_filled.png (a fake student sheet)
"""
import argparse
import json
import random

import cv2
import numpy as np

W, H = 1240, 1754                     # A4 at 150 dpi
MARK, MARGIN = 120, 60


def layout(nq, nc):
    top, left, row_h, col_w = 330, 260, min(120, (H - 500) // nq), 150
    return [[(left + c * col_w, top + q * row_h) for c in range(nc)] for q in range(nq)]


def draw(nq, nc, answers=None):
    img = np.full((H, W), 255, np.uint8)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    corners = [(MARGIN, MARGIN), (W - MARGIN - MARK, MARGIN),
               (W - MARGIN - MARK, H - MARGIN - MARK), (MARGIN, H - MARGIN - MARK)]
    for i, (x, y) in enumerate(corners):
        img[y:y + MARK, x:x + MARK] = cv2.aruco.generateImageMarker(d, i, MARK)
    cv2.putText(img, "Name: ____________________   Class: ______", (220, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
    for q, row in enumerate(layout(nq, nc)):
        cv2.putText(img, f"{q + 1:2d}", (150, row[0][1] + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
        for c, (x, y) in enumerate(row):
            cv2.circle(img, (x, y), 28, 0, 3)
            cv2.putText(img, "ABCDEF"[c], (x - 10, y - 38), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
            if answers and answers[q] == c:
                cv2.circle(img, (x, y), 22, 0, -1)
    return img


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--questions", type=int, default=10)
    p.add_argument("--choices", type=int, default=4)
    a = p.parse_args()
    cv2.imwrite("sheet.png", draw(a.questions, a.choices))
    ans = [random.randrange(a.choices) for _ in range(a.questions)]
    cv2.imwrite("example_filled.png", draw(a.questions, a.choices, ans))
    json.dump({"questions": a.questions, "choices": a.choices, "student_example": ans},
              open("sheet_layout.json", "w"))
    print("sheet.png, example_filled.png, sheet_layout.json  | example answers:", ans)
