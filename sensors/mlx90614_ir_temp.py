"""MLX90614 non-contact infrared thermometer (I2C 0x5A).
Measures surface temperature of motors, bearings, plants, pipes.
It only RECEIVES infrared - it does not emit anything.
pip install adafruit-circuitpython-mlx90614
"""
import random
from common import SIMULATE

_s = None


def read():
    global _s
    if SIMULATE:
        return {"object_c": round(random.gauss(38, 1), 2), "ambient_c": round(random.gauss(26, 0.3), 2)}
    if _s is None:
        import adafruit_mlx90614
        from common.i2c import get_i2c
        _s = adafruit_mlx90614.MLX90614(get_i2c())
    return {"object_c": round(_s.object_temperature, 2), "ambient_c": round(_s.ambient_temperature, 2)}


if __name__ == "__main__":
    print(read())
