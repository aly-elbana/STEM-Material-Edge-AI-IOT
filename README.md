# Capstone Edge AI + IoT Starter Kit

> **From Traditional IoT to Intelligent Edge Systems**  
> A Complete Starting Point for Grade 12 STEM Capstone Projects.

**AI Engineering Department · Faculty of Engineering · Tanta University**

Under the supervision of **Dr. Mahmoud El-Shewimy**, Coordinator of the AI Engineering Department.

**Prepared by:**
- **Eng. Ali Mohamed El-Banna** — Edge AI + IoT
- **Eng. Adham Tarek El-Zarkany** — Raspberry Pi

---

## The Core Idea

### Decide Locally. Report Globally.

The device senses, thinks, and acts locally in milliseconds, without requiring an internet connection. It then reports results to the cloud for monitoring, historical records, and future model improvement.

**الفكرة بالمصري:**

الـ Repository ده نقطة البداية لمشروع الكابستون بتاعك.

هتلاقي فيه:
- أكواد جاهزة للتعامل مع Sensors وMotors.
- أدوات جمع وتجهيز البيانات.
- أدوات تدريب وتقييم الـ Machine Learning Models.
- أدوات تصغير الموديلات وتشغيلها على Edge Devices.
- طرق الربط بالـ Cloud باستخدام MQTT.
- Dashboards لمراقبة النظام.
- Blueprints لمشروعات كاملة تقدر تبدأ منها.

كل حاجة تقدر تجربها على اللابتوب من غير Raspberry Pi باستخدام وضع المحاكاة (Simulation Mode)، وبعد كده تنقل المشروع للـ Raspberry Pi بتغيير إعداد واحد.

ابدأ من قسم **Start Here**، ولو عندك سؤال راجع ملف **Capstone Student Questions** الموجود في مجلد `docs/`.

---

# Table of Contents

1. [Start Here (10 Minutes)](#1-start-here-10-minutes)
2. [What's Inside This Repository?](#2-whats-inside-this-repository)
3. [Which File Answers My Question?](#3-which-file-answers-my-question)
4. [The 8-Step Capstone Workflow](#4-the-8-step-capstone-workflow)
5. [Sensors: Selection, Pins & Addresses](#5-sensors-selection-pins--addresses)
6. [Motors & Actuators](#6-motors--actuators)
7. [Data Collection & Preparation](#7-data-collection--preparation)
8. [Machine Learning Models](#8-machine-learning-models)
9. [YOLO, Quantization & Edge Deployment](#9-yolo-quantization--edge-deployment)
10. [IoT & Cloud Integration](#10-iot--cloud-integration)
11. [Calibration & Performance Evaluation](#11-calibration--performance-evaluation)
12. [Presentation Labs](#12-presentation-labs)
13. [Troubleshooting](#13-troubleshooting)
14. [Safety Guidelines](#14-safety-guidelines)
15. [Contact](#15-contact)

---

# 1. Start Here (10 Minutes)

## Option A: Run Everything on Your Laptop

You don't need a Raspberry Pi to get started. The repository supports hardware simulation by default.

### Installation

```bash
git clone <this-repo-url>
cd capstone-edge-ai-starter

python -m venv .venv
```

Activate the virtual environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run Your First Programs

```bash
python -m blueprints.template.main
```

Press `Ctrl + C` to stop the program and view the response-time summary.

Run a complete simulated system:

```bash
python -m blueprints.conveyor_qc.main
```

**Important:** `SIMULATE=1` is enabled by default.

This means sensors, cameras, and motors are simulated, allowing you to run the scripts without physical hardware.

---

## Option B: Run on Raspberry Pi 5

**Requirements:**
- Raspberry Pi 5
- 64-bit Raspberry Pi OS
- Internet connection for initial installation
- Required sensors and components

### Installation

```bash
git clone <this-repo-url>
cd capstone-edge-ai-starter

bash tools/setup_pi.sh
```

The setup script installs the required system packages, enables I2C/SPI, creates a virtual environment, and installs Python dependencies.

Activate the environment:

```bash
source ~/capstone-env/bin/activate
```

Switch to real hardware mode:

```bash
export SIMULATE=0
```

Check connected hardware:

```bash
python -m tools.check_hardware
```

**Important:**
- Run all commands from the repository root.
- Use `python -m folder.file` instead of executing individual `.py` files directly.

---

# 2. What's Inside This Repository?

The repository is organized into modules, each responsible for a specific part of your project.

```text
capstone-edge-ai-starter/
│
├── common/
│   ├── Shared utilities
│   ├── Simulation switch
│   ├── MQTT client with offline buffering
│   ├── Camera interface
│   ├── Performance timing
│   ├── CSV data logging
│   └── Alert management
│
├── sensors/
│   └── Individual sensor drivers and examples
│
├── motors/
│   ├── DC motor
│   ├── Servo motor
│   ├── Stepper motor
│   ├── Relay / MOSFET
│   ├── RPM encoder
│   └── Motor sizing calculator
│
├── ml/
│   │
│   ├── tabular/
│   │   ├── train_tabular.py
│   │   └── predict_live.py
│   │
│   ├── timeseries/
│   │   ├── features.py
│   │   └── record_fast.py
│   │
│   ├── image/
│   │   ├── train_classifier.py
│   │   └── classify_live.py
│   │
│   ├── yolo/
│   │   ├── train.py
│   │   ├── export.py
│   │   ├── detect_live.py
│   │   └── count_line.py
│   │
│   ├── datasets/
│   │   ├── collect_images.py
│   │   ├── merge_class_folders.py
│   │   ├── merge_yolo_datasets.py
│   │   ├── merge_sensor_csvs.py
│   │   ├── split_dataset.py
│   │   ├── dataset_report.py
│   │   └── augment_images.py
│   │
│   └── quantization/
│       ├── quantize_tflite.py
│       ├── compare_tflite.py
│       ├── quantize_onnx.py
│       └── sklearn_to_onnx.py
│
├── edge/
│   ├── run_tflite.py
│   ├── run_onnx.py
│   └── AI Camera / AI HAT+ documentation
│
├── iot/
│   ├── MQTT publishing / subscribing
│   ├── Mosquitto setup
│   ├── Flask live dashboard
│   ├── ThingSpeak integration
│   ├── Firebase integration
│   └── SQLite history
│
├── calibration/
│   └── calibrate.py
│
├── blueprints/
│   ├── 13 complete project starters
│   └── template/
│
├── labs/
│   ├── part1_raspberry_pi/
│   └── part2_edge_ai/
│
├── tools/
│   ├── setup_pi.sh
│   └── check_hardware.py
│
└── docs/
    ├── Capstone_Student_Questions_EN.pdf
    └── Capstone_Student_Questions_AR.pdf
```

### What Does Each Module Do?

| Module | Purpose |
|---|---|
| `common/` | Shared utilities and system communication |
| `sensors/` | Sensor integration and data acquisition |
| `motors/` | Motor control and actuator management |
| `ml/` | Machine Learning training and evaluation |
| `edge/` | Running trained models on edge devices |
| `iot/` | Cloud communication and dashboards |
| `calibration/` | Sensor calibration and error correction |
| `blueprints/` | Complete project starting points |
| `labs/` | Practical exercises from the presentation |
| `tools/` | Hardware setup and diagnostics |
| `docs/` | Student documentation and FAQs |

---

# 3. Which File Answers My Question?

Use this table to quickly find the right tool for your task.

| Question / Task | Recommended File |
|---|---|
| How do I read a sensor? | `sensors/<sensor>.py` |
| Which motor should I use? | `motors/motor_sizing.py` |
| How do I log data with timestamps? | `common/datalog.py` |
| I only have normal data, no fault samples. | `labs/part2_edge_ai/lab_a_anomaly.py` |
| How do I train a model using CSV data? | `ml/tabular/train_tabular.py` |
| How do I process vibration or motion data? | `ml/timeseries/features.py` |
| How do I classify images? | `ml/image/train_classifier.py` |
| How do I detect and count objects? | `ml/yolo/` |
| How do I combine different datasets? | `ml/datasets/` |
| My model is too slow or too large. | `ml/quantization/` |
| How do I measure response time? | `common/timing.py` |
| How do I send data to a dashboard? | `common/mqtt_client.py` and `iot/` |
| How do I work without internet? | `common/mqtt_client.py` |
| How do I calibrate a sensor? | `calibration/calibrate.py` |
| How do I start a new project? | `blueprints/template/` |

---

# 4. The 8-Step Capstone Workflow

Follow these eight steps to build a complete engineering project.

| Step | Stage | What You Should Do | Evidence for Judges |
|---|---|---|---|
| 1 | Identify the Problem | Define who faces the problem, how often it occurs, and its impact. | Problem statement and references |
| 2 | Define Requirements | Specify response time, accuracy, and two additional measurable requirements. | Requirements table |
| 3 | Select Hardware | Choose suitable sensors, motors, and other components. | Hardware justification |
| 4 | Collect Data | Gather, organize, label, and prepare your dataset. | Dataset and data sheet |
| 5 | Train the Model | Select an appropriate model and train it. | Training notebook and logs |
| 6 | Evaluate Performance | Test the model using a separate, locked test set. | Accuracy, recall, and confusion matrix |
| 7 | Deploy on the Edge | Run the model locally and measure its performance. | Latency measurements |
| 8 | Connect to the Cloud | Integrate MQTT and create a monitoring dashboard. | Live dashboard and system demonstration |

### Important Engineering Requirements

Before purchasing hardware, define measurable requirements.

At minimum, specify:

- Response time.
- Model accuracy.
- Throughput.
- Power consumption or battery life.
- Detection range.
- False alarm rate.

For model evaluation, target:

**Accuracy ≥ 80%**

However, accuracy alone is not sufficient. You must also evaluate recall, precision, and the confusion matrix.

### Recommended Approach

**Build a Thin End-to-End System in Week 1.**

Start with a simple working prototype:

```text
Sensor
   ↓
Rule-Based Decision
   ↓
Buzzer / Actuator
   ↓
MQTT
   ↓
Dashboard
```

Once the complete system works, improve each component individually and introduce Machine Learning where it adds real value.

---

# 5. Sensors: Selection, Pins & Addresses

Choosing the correct sensor is one of the most important engineering decisions.

The following table provides a quick reference for commonly used sensors.

| Measurement | Sensor | Communication / Pins | I2C Address | Repository File |
|---|---|---|---|---|
| Temperature, humidity, pressure | BME280 | I2C (3, 5) | `0x76` | `bme280.py` |
| Analog signals (LDR, soil, gas, pH, TDS, turbidity, flex) | ADS1115 ADC | I2C | `0x48` | `ads1115.py` |
| Distance (2 cm – 4 m) | HC-SR04 | GPIO23/24 | - | `hcsr04.py` |
| Precise distance (3 – 200 cm) | VL53L0X | I2C | `0x29` | `vl53l0x.py` |
| Motion, tilt, vibration, falls | MPU6050 | I2C | `0x68` | `mpu6050.py` |
| UV index and light intensity | LTR390 | I2C | `0x53` | `ltr390_uv.py` |
| Light spectrum and color | AS7341 | I2C | `0x39` | `as7341_spectral.py` |
| Object color detection | TCS34725 | I2C | `0x29` | `tcs34725_color.py` |
| Non-contact surface temperature | MLX90614 | I2C | `0x5A` | `mlx90614_ir_temp.py` |
| Liquid / soil temperature | DS18B20 | 1-Wire (GPIO4) | - | `ds18b20.py` |
| Current, voltage, and power | INA219 | I2C | `0x40` | `ina219_current.py` |
| Weight measurement | Load Cell + HX711 | GPIO5/6 | - | `hx711_load.py` |
| Dust concentration (PM2.5 / PM10) | PMS5003 | UART RX (GPIO15) | - | `pms5003_dust.py` |
| VOC / eCO2 | SGP30 | I2C | `0x58` | `sgp30_air.py` |
| Presence / object detection | PIR, IR Break-Beam, Reed Switch | GPIO | - | `digital_inputs.py` |
| Sound / voice | USB Microphone | USB | - | `microphone.py` |
| Computer Vision | Camera Module 3 / AI Camera / USB Webcam | CSI / USB | - | `common/camera.py` |

### Important Hardware Notes

**1. GPIO Voltage**

Raspberry Pi GPIO pins operate at **3.3V**.

Never connect a 5V output directly to a GPIO input. Use a voltage divider or level shifter when required.

For HC-SR04, the ECHO signal requires a voltage divider.

**2. Analog Inputs**

The Raspberry Pi does not have built-in analog inputs.

Use an external ADC such as ADS1115 to read analog sensors.

**3. I2C Address Conflicts**

Two devices using the same I2C address can create communication conflicts.

For example:
- VL53L0X: `0x29`
- TCS34725: `0x29`

Use a TCA9548A I2C multiplexer when necessary.

**4. Check Connected Devices**

```bash
i2cdetect -y 1
```

### Default GPIO Pin Mapping

The repository uses the following default pin assignments:

| Component | GPIO |
|---|---|
| Buzzer / LED | GPIO27 |
| PIR / IR Beam | GPIO17 |
| Button | GPIO5 |
| Servo | GPIO18 |
| Motor PWM | GPIO12 |
| Motor IN1 / IN2 | GPIO5 / GPIO6 |
| Stepper STEP / DIR / EN | GPIO20 / GPIO21 / GPIO16 |
| Relay | GPIO26 |
| PWM Load | GPIO13 |
| HC-SR04 | GPIO23 / GPIO24 |
| RPM Sensor | GPIO25 |
| I2C SDA / SCL | GPIO2 / GPIO3 |
| UART RX | GPIO15 |

Pin assignments can be changed in the corresponding sensor or motor files.

---

# 6. Motors & Actuators

Different applications require different types of motors and actuators.

Selecting the right component depends on speed, torque, precision, and the mechanical load.

| Application | Recommended Motor | Driver | Notes |
|---|---|---|---|
| Conveyor belts, wheels, mixers | DC Gear Motor (12V, 30–200 RPM) | TB6612FNG / DRV8833 / L298N / BTS7960 | Gearboxes provide higher torque at lower speeds. |
| Precise positioning | Stepper Motor (NEMA17) | A4988 / DRV8825 / TMC2209 | Counts steps to control position. |
| Small positioning tasks | 28BYJ-48 | ULN2003 | Suitable for light loads. |
| Gates, valves, robotic arms | Servo Motor (SG90 / MG90S / MG996R) | Direct signal / PCA9685 | Provides angular positioning. |
| Drones and high-speed fans | BLDC Motor | ESC | Requires careful handling. |
| Fast pushing or locking | 12V Solenoid | MOSFET + Flyback Diode | Fast operation with short pulses. |
| Strong linear movement | Linear Actuator | Relay Pair / H-Bridge | Suitable for pushing and pulling. |
| Liquid movement | DC Pump / Peristaltic Pump | Relay / MOSFET | Peristaltic pumps allow controlled dosing. |
| Silent vibration alerts | Coin Vibration Motor | NPN Transistor / MOSFET | Useful in wearable systems. |
| Switching lamps, heaters, fans | Relay Module | Relay | Mains voltage requires supervision. |

### Motor Sizing

The repository includes a motor sizing calculator.

Run:

```bash
python -m motors.motor_sizing
```

It calculates:

- Conveyor belt force.
- Roller torque (N·m and kg·cm).
- Required RPM.
- Motor power.
- Servo torque for robotic arms.
- Wheel torque for mobile robots.

A safety factor of 2 is included.

### Important Power Rules

- Never power motors directly from the Raspberry Pi 5V pin, except one tiny SG90 during testing.
- Use a separate power supply for motors.
- Connect the grounds together (Common Ground).
- Add a 100–470 µF capacitor near motor drivers.

---

# 7. Data Collection & Preparation

Machine Learning performance depends heavily on data quality.

Before training your model, you need to collect, organize, label, and validate your dataset.

## 7.1 Where Does Data Come From?

### 1. Your Own Hardware (Recommended)

Collect data using your actual sensors and devices.

Available tools:

```text
ml/datasets/collect_images.py
ml/timeseries/record_fast.py
common/datalog.py
```

Blueprints also save collected data inside:

```text
data/*.csv
```

### 2. Controlled Experiments

Create safe experiments to generate different operating conditions.

Examples:
- Add a small weight to a fan to simulate imbalance.
- Block airflow to simulate restricted ventilation.
- Change lighting conditions.
- Add salt to water to change its properties.

### 3. Public Datasets

You can use publicly available datasets from:

- Kaggle
- UCI Machine Learning Repository
- Roboflow Universe
- Open Images
- Edge Impulse Public Projects
- University datasets (e.g., CWRU Bearing Vibration Dataset)

Always check dataset licensing and cite your sources.

### 4. Data Augmentation

Use augmentation to increase training data diversity.

```text
ml/datasets/augment_images.py
```

Apply augmentation to the training split only.

### 5. Synthetic / Simulated Data

You can generate simulated data to get started.

```bash
labs/part2_edge_ai/00_make_data.py
```

Clearly identify simulated data in your project documentation.

---

## 7.2 Data Labeling Tools

| Tool | Main Purpose |
|---|---|
| Roboflow | Image annotation and YOLO datasets |
| Label Studio | Images, audio, text, and other data |
| CVAT | Computer Vision annotation |
| Edge Impulse | Data acquisition, labeling, and training |
| Teachable Machine | Simple image classification |

---

## 7.3 Combining Multiple Datasets

Sometimes you may find two datasets with different class names or structures.

Follow these steps:

1. List all class names from each dataset.
2. Create a mapping table that maps source labels to your project classes.
3. Use the appropriate merging tool.
4. Preserve the source of every sample.
5. Evaluate model performance separately for each source.
6. Fine-tune and test using data collected from your actual device.

### Available Dataset Tools

| Dataset Type | Tool |
|---|---|
| Image Classification | `merge_class_folders.py` |
| YOLO Object Detection | `merge_yolo_datasets.py` |
| Sensor CSV Files | `merge_sensor_csvs.py` |

**Important: Domain Shift**

If your model performs well on Dataset A but poorly on Dataset B, you may have a domain shift problem.

This means the datasets have different distributions or conditions.

The solution is to collect more representative data from your own hardware.

---

## 7.4 Dataset Splitting

Use:

```text
ml/datasets/split_dataset.py
```

A typical split is:

| Dataset Split | Percentage |
|---|---:|
| Training | 70% |
| Validation | 15% |
| Testing | 15% |

These percentages are examples, not mandatory values.

Use `--group-prefix` or `--group` to prevent samples from the same object, person, or recording session from appearing in both training and testing sets.

### Before Training

Run:

```text
ml/datasets/dataset_report.py
```

It checks:
- Class distribution.
- Class imbalance.
- Duplicate samples.
- Broken image files.

---

# 8. Machine Learning Models

Not every problem requires the same Machine Learning approach.

Choose your model based on the type of data and the problem you are trying to solve.

| Data Type | Task | Recommended Starting Point | Repository File |
|---|---|---|---|
| Sensor readings (CSV) | Classification | Random Forest | `ml/tabular/train_tabular.py` |
| Sensor readings (normal data only) | Anomaly Detection | Elliptic Envelope / LOF | `train_tabular.py --mode anomaly` |
| Vibration / Motion / Audio | Classification / Anomaly Detection | Window Features + Random Forest | `ml/timeseries/features.py` |
| Future values (air quality / water level) | Forecasting / Regression | Linear Trend → Random Forest Regressor | `blueprints/air_quality` |
| Images (one label per image) | Image Classification | MobileNetV2 Transfer Learning | `ml/image/train_classifier.py` |
| Multiple objects in images | Object Detection | YOLO26n | `ml/yolo/` |
| Faces / Eyes / Hands / Body | Landmark Detection | MediaPipe Tasks | `blueprints/eye_health`, `posture_coach` |
| Speech / Keywords | Speech Recognition | Vosk / Edge Impulse | `blueprints/pronunciation_coach` |
| Printed Forms / Bubbles | Computer Vision | OpenCV + ArUco | `blueprints/answer_sheet_checker` |
| Natural Language / Chat | Language Processing | Small LLM on AI HAT+ 2 or Cloud LLM API | - |

### An Important Engineering Principle

**Always compare your AI model against a rule-based baseline.**

AI should provide a measurable improvement over simpler solutions to justify its use.

### Model Evaluation

Evaluate your model using:
- Accuracy.
- Precision.
- Recall.
- Confusion Matrix.

Always use a locked test dataset.

**Why does this matter?**

Imagine a dataset containing:

- 1,000 sensor readings.
- Only 10 actual faults.

A model that always predicts "Normal" achieves 99% accuracy but fails to detect every fault.

This is why accuracy alone can be misleading.

---

# 9. YOLO, Quantization & Edge Deployment

Running AI models on devices with limited computational resources requires optimization.

## 9.1 YOLO Object Detection

For object detection, check:

```text
ml/yolo/README.md
```

The repository uses the YOLO26 nano model:

```text
yolo26n.pt
```

For Raspberry Pi 5 CPU deployment, export the model to NCNN:

```bash
python -m ml.yolo.export best.pt --format ncnn --imgsz 320
```

---

## 9.2 Model Quantization

Quantization reduces model size and can improve inference speed.

Available approaches:

| Method | Description |
|---|---|
| FP16 | Uses half-precision floating-point values, reducing model size. |
| INT8 | Uses 8-bit integer representations, potentially reducing model size significantly. |

The repository provides:

```text
ml/quantization/README.md
```

To compare model performance:

```text
compare_tflite.py
```

It reports:
- Model size.
- Inference time.
- Accuracy.

Always re-evaluate accuracy after quantization.

---

## 9.3 Hardware Acceleration

Two available options:

### AI Camera

- Based on Sony IMX500.
- Runs supported AI models inside the camera.
- Can work with different Raspberry Pi models.

### AI HAT+ / AI HAT+ 2

- Uses Hailo AI acceleration.
- Designed for Raspberry Pi 5.

Documentation:

```text
edge/README.md
```

### Recommended Workflow

Train your models on a laptop or Google Colab.

Use the Raspberry Pi primarily for inference and real-time deployment.

---

# 10. IoT & Cloud Integration

An intelligent edge system does not need to depend on the cloud for every decision.

Instead, it can process data locally and send important results to remote monitoring systems.

See:

```text
iot/README.md
```

### Available Tools

| Tool | Purpose |
|---|---|
| MQTT Client | Publish and subscribe to messages |
| Mosquitto | Local MQTT Broker |
| HiveMQ Cloud | Cloud MQTT Broker with TLS |
| Flask Dashboard | Live monitoring dashboard |
| Node-RED | Visual dashboard and automation |
| ThingSpeak | Simple cloud charts |
| SQLite | Local historical data storage |
| Telegram | Mobile alerts |
| Firebase | Backend for mobile applications |

### MQTT Communication

The repository uses:

```text
common/mqtt_client.py
```

Features include:
- JSON message publishing.
- Offline message buffering.
- Reconnection support.

Mosquitto can run locally on the Raspberry Pi, allowing devices to communicate without internet access.

### MQTT Topic Structure

Use the following topic pattern:

```text
stem/<team>/<device>/<what>
```

Example:

```text
stem/team01/pi5/temperature
stem/team01/pi5/fault
stem/team01/conveyor/status
```

### Security

- Store passwords in environment variables.
- Use `.env.example` as a configuration template.
- Never hardcode credentials inside your source code.

---

# 11. Calibration & Performance Evaluation

A successful engineering project must prove that its requirements are actually met.

Use measurable tests instead of relying on assumptions.

| Requirement | How to Prove It |
|---|---|
| Response Time | Use `LatencyLog` and measure mean, p95, and worst-case latency. |
| AI Accuracy ≥ 80% | Use a locked test set and display the confusion matrix. |
| Sensor Calibration | Compare sensor readings against a reference instrument. |
| Wireless Communication | Demonstrate a live dashboard. |
| System Responsiveness | Change an input and show the corresponding output. |
| Reliability | Perform repeated tests under different operating conditions. |
| Power Consumption | Use INA219 to record power measurements. |
| Portability | Demonstrate the complete system inside its enclosure. |

### Response Time Measurement

Every blueprint generates latency measurements:

```text
*_latency.csv
```

Measure:

- Mean latency.
- P95 latency.
- Worst-case latency.

Use at least 20 runs.

### Sensor Calibration

Run:

```bash
python -m calibration.calibrate
```

The calibration tool compares sensor readings against reference measurements and generates correction data and plots.

---

# 12. Presentation Labs

The repository includes the practical labs covered in the presentation.

## Part 1: Raspberry Pi

Location:

```text
labs/part1_raspberry_pi/
```

Included exercises:

1. LED + Button.
2. BME280.
3. LDR + ADS1115.
4. HC-SR04 with Voltage Divider.
5. Smart Classroom Logger.

## Part 2: Edge AI

Location:

```text
labs/part2_edge_ai/
```

Included exercises:

| Lab | Topic |
|---|---|
| M3 Example | Generate a sample dataset |
| Lab A | Anomaly Detection |
| Lab B | Honest Model Evaluation |
| Lab C | LiteRT on Edge + Performance Timing |
| Lab D | MQTT Communication |
| Lab E | Complete Sense–Think–Act–Report System |
| Bonus | Compare Different Detection Algorithms |

### Run the Edge AI Labs

```bash
cd labs/part2_edge_ai

python 00_make_data.py

python lab_a_anomaly.py
```

---

# 13. Troubleshooting

Common problems and their possible solutions.

| Problem | Possible Cause | Recommended Solution |
|---|---|---|
| `i2cdetect` shows no devices | I2C disabled or incorrect wiring | Enable I2C using `raspi-config` and check SDA/SCL connections. |
| Raspberry Pi reboots when the motor starts | Motor powered directly from the Pi or insufficient power supply | Use a separate motor supply, common ground, and a capacitor. |
| Sensor readings fluctuate | Electrical noise or poor connections | Average readings, shorten wires, and calibrate the sensor. |
| `ModuleNotFoundError: common` | Running scripts from the wrong directory | Run commands from the repository root using `python -m`. |
| Picamera2 not found in virtual environment | System packages unavailable inside the virtual environment | Create the environment using `--system-site-packages`. |
| Servo jitters | Power instability or PWM issues | Use hardware PWM or PCA9685 and a separate power supply. |
| Model performs well during training but poorly on hardware | Overfitting or different operating conditions | Collect representative device data and evaluate using a locked test set. |
| YOLO inference is slow | Model is too computationally expensive | Export to NCNN, reduce image size, or use hardware acceleration. |
| MQTT connection fails | Incorrect host, port, or TLS configuration | Check network settings or use a local Mosquitto broker. |
| Project works at home but fails during exhibition | Different lighting or Wi-Fi conditions | Test under exhibition conditions and prepare a local broker. |

### Raspberry Pi 5 Power Note

A Raspberry Pi 5 generally requires a suitable 5V power supply rated for up to 5A for recommended operation.

---

# 14. Safety Guidelines

Safety is an essential part of engineering.

Follow these rules throughout hardware development and testing.

### Electrical Safety

- Raspberry Pi GPIO operates at 3.3V only.
- Use voltage dividers or level shifters for 5V signals.
- Never connect incompatible voltage levels directly.

### Motors & Mechanical Components

- Use separate power supplies for motors, pumps, and solenoids.
- Use flyback protection where required.
- Ensure common ground between the Raspberry Pi and motor drivers.
- Never touch moving conveyor belts or exposed propellers.

### Mains Electricity

- 220V AC experiments must only be performed under teacher supervision and inside a properly enclosed box.
- Prefer ready-made smart plugs or low-voltage alternatives.

### Health-Related Projects

- Eye and health projects should be measurement-only.
- Never shine UV, IR, or intense light directly into people's eyes.
- Do not claim medical diagnostic capabilities.
- Obtain consent before recording people.

### Batteries

- Use appropriate chargers and battery protection boards for Li-ion batteries.
- Never short-circuit, puncture, or physically damage batteries.

### Experimental Safety

- Never cause real machine damage to collect fault data.
- Never perform uncontrolled fall experiments.
- Use safe, controlled, supervised experiments.

---

# 15. Contact

For questions about the starter kit, technical support, or your capstone idea:

**Eng. Ali Mohamed El-Banna**

AI Engineering Department  
Faculty of Engineering  
Tanta University

**Phone / WhatsApp:** 01099133031

---

## Final Note

Your capstone is not just about building an AI model.

It is about engineering a complete system that can:

**Sense → Think → Act → Communicate → Improve**

Start simple, measure everything, test your assumptions, and build something that solves a real problem.
