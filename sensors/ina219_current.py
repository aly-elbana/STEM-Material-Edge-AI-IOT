"""INA219 current + voltage + power (I2C 0x40). Measure a motor's current
(health / overload), or your project's power consumption (a great extra requirement).
Wire it IN SERIES with the load's + wire (Vin+ from supply, Vin- to load).
pip install adafruit-circuitpython-ina219
"""
import random
from common import SIMULATE

_s = None


def read():
    global _s
    if SIMULATE:
        return {"bus_v": round(random.gauss(12, 0.05), 3), "current_ma": round(random.gauss(420, 15), 1),
                "power_mw": round(random.gauss(5000, 150), 1)}
    if _s is None:
        from adafruit_ina219 import INA219
        from common.i2c import get_i2c
        _s = INA219(get_i2c())
    return {"bus_v": round(_s.bus_voltage, 3), "current_ma": round(_s.current, 1),
            "power_mw": round(_s.power * 1000, 1)}


if __name__ == "__main__":
    print(read())
