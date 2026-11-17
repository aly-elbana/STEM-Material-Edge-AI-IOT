"""TCS34725 RGB colour sensor (I2C 0x29) - colour sorting on a conveyor, ripeness.
Put the object 1-2 cm away, keep the LED on, and shield from room light.
pip install adafruit-circuitpython-tcs34725
NOTE: same address (0x29) as VL53L0X - do not put both on one bus without a mux.
"""
import random
from common import SIMULATE

_s = None


def read():
    global _s
    if SIMULATE:
        return {"r": random.randint(0, 255), "g": random.randint(0, 255),
                "b": random.randint(0, 255), "lux": round(random.uniform(50, 300), 1)}
    if _s is None:
        import adafruit_tcs34725
        from common.i2c import get_i2c
        _s = adafruit_tcs34725.TCS34725(get_i2c())
        _s.integration_time = 50
        _s.gain = 4
    r, g, b = _s.color_rgb_bytes
    return {"r": r, "g": g, "b": b, "lux": round(_s.lux or 0, 1)}


if __name__ == "__main__":
    print(read())
