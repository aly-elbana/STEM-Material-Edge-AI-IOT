"""HC-SR04 ultrasonic distance (2 cm - 4 m). It is a 5 V sensor:
ECHO must go through a divider: ECHO -> 330R -> GPIO24 -> 470R -> GND  (= 2.94 V).
TRIG -> GPIO23. VCC -> 5 V, GND -> GND.
Tip: for short, precise, quiet ranges prefer the VL53L0X laser (sensors/vl53l0x.py).
"""
import random
from common import SIMULATE

_s = None


def read_cm(echo=24, trigger=23):
    global _s
    if SIMULATE:
        return round(random.uniform(40, 160), 1)
    if _s is None:
        from gpiozero import DistanceSensor
        _s = DistanceSensor(echo=echo, trigger=trigger, max_distance=4)
    return round(_s.distance * 100, 1)


if __name__ == "__main__":
    import time
    while True:
        print(read_cm(), "cm")
        time.sleep(0.3)
