"""ADS1115: 4-channel 16-bit ADC. The Pi has NO analog input - use this for
LDR, soil moisture, gas (MQ-x), pH, TDS, turbidity, potentiometers, flex sensors...
Wiring: VDD->3V3, GND->GND, SDA->pin 3, SCL->pin 5, address 0x48.
NEVER feed more than VDD (3.3 V) into A0-A3: use a voltage divider for 5 V sensors.
pip install adafruit-circuitpython-ads1x15
"""
import random
from common import SIMULATE

_ads = None
_ch = {}


def read(channel=0, address=0x48):
    """Returns (voltage_V, raw_value)."""
    global _ads
    if SIMULATE:
        v = round(random.uniform(1.2, 1.4), 4)
        return v, int(v / 4.096 * 32767)
    if _ads is None:
        import adafruit_ads1x15.ads1115 as ADS
        from common.i2c import get_i2c
        _ads = ADS.ADS1115(get_i2c(), address=address)
    if channel not in _ch:
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
        try:
            pin = [ADS.P0, ADS.P1, ADS.P2, ADS.P3][channel]   # library v2
        except AttributeError:
            pin = channel                                      # library v3
        _ch[channel] = AnalogIn(_ads, pin)
    a = _ch[channel]
    return round(a.voltage, 4), a.value


def percent(voltage, v_dry, v_wet):
    """Map a voltage to 0-100 % between two calibration points (e.g. soil sensor
    in dry air vs in water). Calibrate v_dry/v_wet yourself!"""
    p = (voltage - v_dry) / (v_wet - v_dry) * 100.0
    return max(0.0, min(100.0, p))


if __name__ == "__main__":
    for ch in range(4):
        print("A%d" % ch, read(ch))
