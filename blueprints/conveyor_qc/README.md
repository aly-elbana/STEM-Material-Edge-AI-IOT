# Conveyor QC (industrial pathway)

**Problem:** a person cannot inspect every item; bad items reach customers.
**System:** belt moves items -> IR beam detects an item -> camera photo -> model says good/defective
-> servo pushes defective items off -> counts + rates go to the dashboard.

## Parts
| Part | Choice | Why |
|---|---|---|
| Belt motor | 12 V DC **gear** motor (e.g. 30-100 rpm) + TB6612FNG / L298N / BTS7960 | continuous speed, high torque at low rpm |
| Indexed belt (stop at each item) | NEMA17 stepper + A4988/TMC2209 | exact positioning, no encoder needed |
| Reject | MG996R servo (or SG90 for light items) / 12 V push solenoid + MOSFET + diode | servo = gentle push; solenoid = fast |
| Item detection | IR break-beam pair (best) or IR obstacle module / VL53L0X | trigger the photo at the same spot every time |
| Inspection | Pi Camera (+ fixed LED light!) or TCS34725 for colour-only sorting | constant light = stable accuracy |
| Speed measurement | slotted optical encoder or Hall + magnet | prove the belt speed requirement |
| Weight check (optional) | load cell + HX711 under a section | under/over-filled packages |

Use `python -m motors.motor_sizing` to compute the torque for your load and roller.

## Wiring (default pins in the code)
IR beam OUT -> GPIO17 · servo signal -> GPIO18 · motor driver PWM -> GPIO12, IN1 -> GPIO5, IN2 -> GPIO6 ·
servo + motor power from a **separate** 5 V / 12 V supply, **common ground** with the Pi.

## Build the model
1. `python -m ml.datasets.collect_images --label good --count 200` (and each defect class), ON the belt, with the final lighting.
2. `python -m ml.datasets.split_dataset dataset_raw --out split`
3. `python -m ml.image.train_classifier split` (laptop/Colab) -> `model_fp16.tflite`, report, confusion matrix.
   Or detect several items at once with YOLO (`ml/yolo`) and count with `ml/yolo/count_line.py`.

## Requirements to measure (examples)
| Requirement | Target | How (file) |
|---|---|---|
| Response time beam -> decision | <= 300 ms | `conveyor_latency.csv` (mean / p95 / worst) |
| Accuracy on test set | >= 85 %, recall(defective) >= 90 % | `report.txt` from training |
| Throughput | >= 30 items / min | status topic `throughput_per_min` |
| False rejects | <= 5 % of good items | confusion matrix / `data/conveyor.csv` |
| Belt speed | 0.10 m/s +- 5 % | `motors/encoder_rpm.py` |

## Common mistakes
Light changes (cover the inspection area, add an LED strip) · motion blur (higher shutter speed, slower belt)
· pusher timing (measure `--travel-s` with a stopwatch / the log) · motor noise resetting the Pi (separate supply, capacitor, common ground).
