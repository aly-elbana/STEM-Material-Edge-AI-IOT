"""AS7341 11-channel spectral sensor (I2C 0x39): violet->red + clear + NIR.
Useful for "how much BLUE light reaches the eyes from screens", colour sorting,
plant light, fruit ripeness.
pip install adafruit-circuitpython-as7341
"""
import random
from common import SIMULATE

_s = None
BANDS = ["415nm", "445nm", "480nm", "515nm", "555nm", "590nm", "630nm", "680nm"]


def read():
    global _s
    if SIMULATE:
        vals = {b: int(random.uniform(200, 900)) for b in BANDS}
        vals["clear"] = sum(vals.values()) // 3
        vals["nir"] = int(random.uniform(50, 200))
        return vals
    if _s is None:
        import adafruit_as7341
        from common.i2c import get_i2c
        _s = adafruit_as7341.AS7341(get_i2c())
    vals = {b: getattr(_s, "channel_" + b) for b in BANDS}
    vals["clear"] = _s.channel_clear
    vals["nir"] = _s.channel_nir
    return vals


def blue_ratio(v):
    """Share of blue (415-480 nm) in the visible bands: 0..1.
    A RELATIVE indicator for your project, not a medical measurement."""
    blue = v["415nm"] + v["445nm"] + v["480nm"]
    total = sum(v[b] for b in BANDS) or 1
    return blue / total


if __name__ == "__main__":
    v = read()
    print(v, "blue ratio:", round(blue_ratio(v), 3))
