"""Train YOLO on YOUR labelled data (laptop with GPU, or Google Colab).

    pip install ultralytics
    python -m ml.yolo.train yolo_split/data.yaml --model yolo26n.pt --epochs 50 --imgsz 640

data.yaml (made by split_dataset.py --yolo):
    path: /abs/path/yolo_split
    train: train/images
    val: val/images
    test: test/images
    names: {0: good, 1: cap_missing}

Results: runs/detect/<name>/weights/best.pt  + results.png + confusion_matrix.png
Metric to report: mAP50 (and per-class precision/recall) on the TEST split:
    python -m ml.yolo.train data.yaml --validate-only runs/detect/train/weights/best.pt
"""
import argparse

from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("data")
p.add_argument("--model", default="yolo26n.pt", help="start from pretrained weights (transfer learning)")
p.add_argument("--epochs", type=int, default=50)
p.add_argument("--imgsz", type=int, default=640)
p.add_argument("--batch", type=int, default=16)
p.add_argument("--name", default="train")
p.add_argument("--validate-only", help="path to best.pt: just evaluate on the test split")
a = p.parse_args()

if a.validate_only:
    m = YOLO(a.validate_only)
    r = m.val(data=a.data, split="test", imgsz=a.imgsz)
    print("TEST mAP50:", round(r.box.map50, 3), " mAP50-95:", round(r.box.map, 3))
else:
    m = YOLO(a.model)
    m.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, name=a.name,
            patience=15)   # stops early if validation stops improving (fights overfitting)
    print("best weights: runs/detect/%s/weights/best.pt" % a.name)
