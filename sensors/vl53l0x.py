"""VL53L0X time-of-flight laser distance, I2C (address 0x29), ~3-200 cm.
Precise, narrow beam, works in silence - good for screen distance, obstacles, fill level.
pip install adafruit-circuitpython-vl53l0x
"""
import random
from common import SIMULATE

_d = None


def read_cm():
    global _d
    if SIMULATE:
        return round(random.gauss(55, 6), 1)
    if _d is None:
        import adafruit_vl53l0x
        from common.i2c import get_i2c
        _d = adafruit_vl53l0x.VL53L0X(get_i2c())
    return round(_d.range / 10.0, 1)   # .range is in mm


if __name__ == "__main__":
    print(read_cm(), "cm")
