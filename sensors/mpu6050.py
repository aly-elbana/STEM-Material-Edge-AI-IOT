"""MPU6050 accelerometer + gyroscope (I2C 0x68). Vibration, tilt, falls, motion.
pip install adafruit-circuitpython-mpu6050
Sampling tip: for vibration analysis read fast and evenly (e.g. 200-500 Hz) and
record the real sample rate - see ml/timeseries/features.py.
"""
import math
import random
from common import SIMULATE

_m = None


def read():
    """Returns dict: ax, ay, az (m/s^2), gx, gy, gz (rad/s)."""
    global _m
    if SIMULATE:
        return {"ax": random.gauss(0, 0.3), "ay": random.gauss(0, 0.3),
                "az": random.gauss(9.81, 0.3), "gx": random.gauss(0, 0.05),
                "gy": random.gauss(0, 0.05), "gz": random.gauss(0, 0.05)}
    if _m is None:
        import adafruit_mpu6050
        from common.i2c import get_i2c
        _m = adafruit_mpu6050.MPU6050(get_i2c())
    ax, ay, az = _m.acceleration
    gx, gy, gz = _m.gyro
    return {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz}


def magnitude(r):
    return math.sqrt(r["ax"] ** 2 + r["ay"] ** 2 + r["az"] ** 2)


if __name__ == "__main__":
    r = read()
    print(r, "|a| =", round(magnitude(r), 2))
