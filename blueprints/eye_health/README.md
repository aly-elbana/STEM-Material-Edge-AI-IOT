# Eye health assistant (medical pathway - safe, no diagnosis)

**Problem:** long screen/study time, short distance, few blinks, poor light and UV strain the eyes.
**System:** measure those factors continuously, remind the user at the right moment, report daily
statistics to a parent/teacher dashboard.

> **Safety first:** the device **measures** light (UV, blue, lux). It must **never emit** UV, IR,
> lasers or bright light toward the eyes. VL53L0X is a Class 1 eye-safe laser, but still do not
> aim it at eyes on purpose. The capstone forbids medical projects that put anyone at risk, and
> the device gives habit reminders, not medical advice.

## What to measure and with what
| Factor | Sensor | Threshold idea (cite a source in your poster) |
|---|---|---|
| Distance to screen | Camera face-width (MediaPipe) or VL53L0X | < 50 cm for > 10 s |
| Break time | timer | 20-20-20 rule |
| Blink rate | Camera + MediaPipe Face Landmarker (EAR) | < 10 blinks / min |
| Room light | LTR390 (lux) | < 300 lux for reading |
| Blue light share | AS7341 (415-480 nm vs visible) | relative, e.g. night-time high share |
| UV outdoors | LTR390 (UV index) | UVI >= 3 -> sunglasses |

## Where is the AI (>= 80 % accuracy requirement)?
Pick one (or more) and evaluate it on a **locked test set**:
1. **Blink / eye-state detector** - label frames open vs closed (record yourself + classmates, with consent).
   Compare EAR threshold vs a small CNN on eye crops (`ml/image/train_classifier.py`). Report accuracy + recall of "closed".
2. **Distance estimator** - camera face width -> distance; error vs a tape measure (regression, report mean error in cm).
3. **Context classifier** - from lux + blue ratio + UV + time: "screen / reading / outdoors" (`ml/tabular/train_tabular.py`).

## Wiring
VL53L0X, LTR390, AS7341 all on I2C (pins 3/5, 3V3, GND) - different addresses (0x29, 0x53, 0x39), so they share the bus.
Buzzer -> GPIO27. Camera on the CSI port (or USB webcam).

## Run
```bash
python -m blueprints.eye_health.main                       # simulation
pip install mediapipe && wget -O face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
SIMULATE=0 python -m blueprints.eye_health.main --camera --lang ar
```

## Requirements to measure (examples)
| Requirement | Target | Proof |
|---|---|---|
| Eye-state accuracy | >= 85 % on test frames | confusion matrix |
| Distance error | <= 5 cm at 30-80 cm | table vs tape measure |
| Reminder latency | <= 1 s after the condition persists | `eye_latency.csv` |
| Battery life (if wearable/desk unit) | >= 4 h | INA219 / USB power meter log |
