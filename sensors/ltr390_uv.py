"""LTR390 UV + ambient light sensor (I2C 0x53).
.uvi = UV index (sunlight). .lux = ambient light.
pip install adafruit-circuitpython-ltr390
Safety: this MEASURES UV. Never build a project that shines UV or IR into eyes.
"""
import random
from common import SIMULATE

_s = None


def read():
    global _s
    if SIMULATE:
        return {"uv_index": round(max(0, random.gauss(2.5, 1.5)), 2),
                "lux": round(random.uniform(150, 800), 1)}
    if _s is None:
        import adafruit_ltr390
        from common.i2c import get_i2c
        _s = adafruit_ltr390.LTR390(get_i2c())
    return {"uv_index": round(_s.uvi, 2), "lux": round(_s.lux, 1)}


if __name__ == "__main__":
    print(read())
