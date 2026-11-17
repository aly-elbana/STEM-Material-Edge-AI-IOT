# Blueprints: one starting point per project type

Every blueprint follows **Sense -> Think -> Act -> Report**, runs in simulation on a laptop
(`SIMULATE=1`, default) and on the Pi with real hardware (`SIMULATE=0`).
Run from the repo root:  `python -m blueprints.<name>.main`

| Blueprint | Pathway | Sensors / inputs | AI part | Outputs |
|---|---|---|---|---|
| `template` | any | anything | rule -> model | buzzer + MQTT |
| `conveyor_qc` | industrial | IR beam, camera, encoder | defect classifier / YOLO | belt motor, servo reject, counts |
| `machine_health` | industrial | MPU6050, INA219, MLX90614 | anomaly detection on vibration windows | alarm, dashboard |
| `smart_agriculture` | industrial / agri | soil moisture, BME280, LTR390 | irrigation decision model | pump with safety limits |
| `air_quality` | medical / environment | PMS5003, SGP30, BME280 | 15-min PM2.5 forecast | purifier fan |
| `water_quality` | medical / environment | pH, TDS, turbidity, DS18B20 | safe / check classifier | dashboard |
| `eye_health` | medical | camera (blink, distance), VL53L0X, LTR390 (UV, lux), AS7341 (blue) | eye-state / distance / context models | voice + buzzer reminders |
| `posture_coach` | medical / education | camera (MediaPipe pose) | slouch classifier | voice reminder |
| `fall_detection` | medical | MPU6050 (wearable) | fall vs daily activity classifier | Telegram alert + cancel button |
| `assistive_glasses` | medical | camera + ToF/ultrasonic | YOLO object detection | voice + vibration |
| `smart_classroom` | educational | PIR, camera, BME280, SGP30, LTR390 | occupancy (camera + PIR fusion) | lights, fan |
| `pronunciation_coach` | educational | microphone | offline speech recognition (Vosk) + scoring | teacher dashboard |
| `answer_sheet_checker` | educational | camera | computer vision (ArUco + bubble reading) | scores + class stats |
| `smart_parking` | industrial / city | camera | YOLO vehicle detection | free spots |

Not your idea? Copy `template/` and combine pieces from `sensors/`, `motors/`, `ml/`, `iot/`.
