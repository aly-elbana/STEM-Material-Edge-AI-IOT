# YOLO on the Raspberry Pi (Ultralytics)

YOLO = object **detection**: *what* is in the picture and *where* (boxes).
Current family: **YOLO26** (`yolo26n.pt` = nano, the one for the Pi). `yolo11n.pt` also works.

| Step | Where | Command |
|---|---|---|
| 1. Try a ready model | Pi or laptop | `python -m ml.yolo.detect_live --model yolo26n.pt` |
| 2. Label your images | browser | Roboflow / Label Studio / CVAT -> export **YOLO** format |
| 3. Merge / split | laptop | `ml/datasets/merge_yolo_datasets.py`, `split_dataset.py --yolo` |
| 4. Train | laptop / **Colab GPU** | `python -m ml.yolo.train data.yaml --epochs 50` |
| 5. Export for the Pi | anywhere | `python -m ml.yolo.export runs/detect/train/weights/best.pt --format ncnn` |
| 6. Run + time it | Pi | `python -m ml.yolo.detect_live --model best_ncnn_model` |
| 7. Count objects crossing a line | Pi | `python -m ml.yolo.count_line --model best_ncnn_model` |

**Formats** (export.py): `ncnn` (fastest on Pi 5 CPU), `onnx`, `tflite` (+ `--int8`),
`imx` (Raspberry Pi AI Camera), `hef` (Hailo AI HAT+: compile with Hailo's tools / Model Zoo).

Install on the Pi (64-bit OS, inside a venv): `pip install ultralytics` (export extras install on first export).
Expect on Pi 5 CPU with the nano model at 640: a few FPS; use `--imgsz 320` for ~3-4x more speed,
or the AI HAT+ / AI Camera for real-time (~30 FPS).
