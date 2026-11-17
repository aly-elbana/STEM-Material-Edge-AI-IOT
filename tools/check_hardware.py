"""Quick health check of everything connected (run on the Pi with SIMULATE=0).
    SIMULATE=0 python -m tools.check_hardware
"""
import importlib
import platform
import shutil
import subprocess

print("Python", platform.python_version(), "|", platform.machine())
if shutil.which("i2cdetect"):
    out = subprocess.run(["i2cdetect", "-y", "1"], capture_output=True, text=True).stdout
    found = sorted({tok for line in out.splitlines()[1:] for tok in line.split()[1:] if tok not in ("--", "UU")})
    known = {"76": "BME280", "77": "BME280(alt)", "48": "ADS1115", "29": "VL53L0X/TCS34725",
             "68": "MPU6050", "53": "LTR390", "39": "AS7341", "5a": "MLX90614", "40": "INA219/PCA9685",
             "58": "SGP30", "62": "SCD4x", "3c": "OLED SSD1306"}
    print("I2C devices:", [f"0x{a} {known.get(a, '?')}" for a in found] or "none")
for mod in ["sensors.bme280", "sensors.ads1115", "sensors.vl53l0x", "sensors.mpu6050", "sensors.ltr390_uv"]:
    try:
        m = importlib.import_module(mod)
        fn = getattr(m, "read", None) or getattr(m, "read_cm")
        print(f"{mod:22s} OK  {fn()}")
    except Exception as e:
        print(f"{mod:22s} --  {type(e).__name__}: {e}")
try:
    from common.camera import Camera
    c = Camera()
    print("camera:", c.kind, c.read().shape)
    c.close()
except Exception as e:
    print("camera: --", e)
