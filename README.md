# M3 Edge AI Labs — Capstone 2026/27
Faculty of Engineering, Tanta University · AI Engineering Department
Eng. Adham Tarek El-Zarkany (Part 1) · Eng. Ali Mohamed El-Banna (Part 2)

> M3 is a **fictional** motor in a juice factory that we used as a running example.
> Replace it with your own project: the code stays almost the same.

## الكود ده إيه؟
ده الكود الكامل اللي شفتوه في البرزنتيشن. كل ملف بيشتغل لوحده.
- **part2_edge_ai** بيشتغل على أي لابتوب (Windows / Mac / Linux) أو على Raspberry Pi، **من غير أي حساسات**.
- **part1_raspberry_pi** محتاج Raspberry Pi والحساسات متوصلة زي رسومات الأسلاك في البرزنتيشن.

## Setup (once)
```bash
pip install -r requirements.txt
```
(On Raspberry Pi OS use a virtual environment: `python3 -m venv --system-site-packages env && source env/bin/activate`)

## Part 2 — Edge AI (run in this order, inside `part2_edge_ai/`)
| File | What it does | Slide |
|---|---|---|
| `00_make_data.py` | Creates practice data: `m3_normal.csv`, `m3_labeled.csv` | — |
| `lab_a_anomaly.py` | Learns "normal" from normal data only, flags strange readings | Lab A |
| `lab_b_evaluate.py` | Train/test split, confusion matrix, precision/recall | Lab B |
| `lab_c_litert.py` | Runs `m3_model.tflite` with LiteRT and times it in ms | Lab C |
| `lab_c_export_model.py` | (Optional, needs TensorFlow) re-creates the .tflite model | Lab C |
| `lab_d_mqtt.py` | Sends M3's status over MQTT to a public **test** broker | Lab D |
| `lab_e_loop.py` | The full loop: sense → think → act → report (works offline) | Lab E |
| `bonus_compare_detectors.py` | Why we test models before trusting them | — |

```bash
cd part2_edge_ai
python 00_make_data.py
python lab_a_anomaly.py
```

## Part 1 — Raspberry Pi (inside `part1_raspberry_pi/`)
| File | Hardware |
|---|---|
| `lab1_led_button.py` | LED on GPIO27 (pin 13) + 330 Ω, button on GPIO5 (pin 29) |
| `lab2_bme280.py` | BME280 on I²C, address 0x76 (enable I²C first) |
| `lab3_ldr_ads1115.py` | LDR + 10 kΩ into ADS1115 A0, address 0x48 |
| `lab4_distance.py` | HC-SR04 — **use the 330 Ω / 470 Ω divider on ECHO** |
| `room_logger.py` | BME280 + PIR on GPIO17 → `room_log.csv` |

## For your own project
1. Log your own data with `room_logger.py` (one row per second, time + units).
2. Put your column names instead of `temp, vibration, current`.
3. Start with Lab A (normal data only). Collect labelled faults later for Lab B.
4. Always report results on **test data**, never on training data.

## Safety
- GPIO is **3.3 V only**. Never connect a 5 V signal directly.
- Never drive motors or relays from GPIO directly: use a driver / relay module.
- The public MQTT test broker is visible to everyone: no real or private data.
