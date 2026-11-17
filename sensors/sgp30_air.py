"""SGP30 air quality (I2C 0x58): eCO2 (ppm) and TVOC (ppb).
Needs ~15 s warm-up and ~12 h to settle its baseline. eCO2 is ESTIMATED from VOCs;
for real CO2 use an SCD40/SCD41 (adafruit-circuitpython-scd4x).
pip install adafruit-circuitpython-sgp30
"""
import random
from common import SIMULATE

_s = None


def read():
    global _s
    if SIMULATE:
        return {"eco2_ppm": random.randint(450, 1400), "tvoc_ppb": random.randint(10, 300)}
    if _s is None:
        import adafruit_sgp30
        from common.i2c import get_i2c
        _s = adafruit_sgp30.Adafruit_SGP30(get_i2c())
        _s.iaq_init()
    return {"eco2_ppm": _s.eCO2, "tvoc_ppb": _s.TVOC}


if __name__ == "__main__":
    print(read())
