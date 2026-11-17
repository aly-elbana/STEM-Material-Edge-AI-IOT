# Running models on the edge: which runtime for which model?

| Model you have | Runtime on the Pi | Script |
|---|---|---|
| scikit-learn (`model.joblib`) | scikit-learn | `ml/tabular/predict_live.py` |
| Keras / Teachable Machine / Edge Impulse (`.tflite`) | LiteRT (`pip install ai-edge-litert`) | `edge/run_tflite.py`, `ml/image/classify_live.py` |
| ONNX (`.onnx`) from PyTorch / sklearn / YOLO | onnxruntime | `edge/run_onnx.py` |
| YOLO (`best.pt`) | Ultralytics -> export **NCNN** | `ml/yolo/detect_live.py` |
| Edge Impulse project | `edge-impulse-linux-runner` or the Linux Python SDK | edgeimpulse.com docs |
| AI Camera (Sony IMX500) | model runs **inside the camera**; Picamera2 IMX500 examples | see below |
| AI HAT+ / AI HAT+ 2 (Hailo) | HailoRT + `.hef` model; Raspberry Pi / Hailo example apps | see below |

## AI Camera (IMX500) quick test
```bash
sudo apt install imx500-all
rpicam-hello -t 0s --post-process-file /usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json --viewfinder-width 1920 --viewfinder-height 1080 --framerate 30
```
Your own YOLO: `python -m ml.yolo.export best.pt --format imx --data data.yaml`, then follow the
Picamera2 `examples/imx500` scripts (object detection demo takes `--model network.rpk --labels labels.txt`).

## AI HAT+ (Hailo) quick test
```bash
sudo apt install hailo-all     # AI HAT+ 13/26 TOPS   (AI HAT+ 2: follow its own docs)
sudo reboot
hailortcli fw-control identify
```
Then clone Hailo's Raspberry Pi examples repo (hailo-apps / hailo-rpi5-examples) and run the detection
demo. Custom models must be compiled to `.hef` with the Hailo Dataflow Compiler (on an x86 PC)
or taken ready from the Hailo Model Zoo.

## Always measure
`common/timing.py -> benchmark(fn)` gives mean / p95 / worst ms. Report the worst case too.
