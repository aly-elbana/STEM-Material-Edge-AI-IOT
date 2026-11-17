"""BME280: temperature (C), humidity (%), pressure (hPa) over I2C.
Wiring: VIN->3V3 (pin 1), GND->pin 6, SDA->pin 3, SCL->pin 5. Address 0x76 (or 0x77).
pip install adafruit-circuitpython-bme280
"""
import random
from common import SIMULATE

_dev = None


def read(address=0x76):
    global _dev
    if SIMULATE:
        return {"temp_c": round(random.gauss(26, 0.4), 2),
                "humidity": round(random.gauss(50, 2), 1),
                "pressure_hpa": round(random.gauss(1012, 1), 1)}
    if _dev is None:
        from adafruit_bme280 import basic as adafruit_bme280
        from common.i2c import get_i2c
        _dev = adafruit_bme280.Adafruit_BME280_I2C(get_i2c(), address=address)
    return {"temp_c": round(_dev.temperature, 2),
            "humidity": round(_dev.relative_humidity, 1),
            "pressure_hpa": round(_dev.pressure, 1)}


if __name__ == "__main__":
    print(read())
