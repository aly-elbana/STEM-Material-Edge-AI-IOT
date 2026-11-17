"""Measure motor / belt speed: slotted optical sensor or Hall sensor + magnet.
Gives you a real number for requirements like "belt speed 0.2 m/s +-5 %".
Wiring: sensor OUT -> GPIO25 (3.3 V logic!), VCC -> 3V3, GND -> GND.
"""
import threading
import time
from common import SIMULATE


class RPMMeter:
    def __init__(self, pin=25, pulses_per_rev=1):
        self.ppr = pulses_per_rev
        self.count = 0
        self._lock = threading.Lock()
        if not SIMULATE:
            from gpiozero import DigitalInputDevice
            self.sensor = DigitalInputDevice(pin, pull_up=True)
            self.sensor.when_activated = self._tick

    def _tick(self):
        with self._lock:
            self.count += 1

    def rpm(self, window=1.0):
        if SIMULATE:
            return 120.0
        with self._lock:
            self.count = 0
        time.sleep(window)
        with self._lock:
            pulses = self.count
        return pulses / self.ppr / window * 60.0


def belt_speed_m_s(rpm, roller_diameter_m):
    return rpm / 60.0 * 3.14159 * roller_diameter_m


if __name__ == "__main__":
    r = RPMMeter(pulses_per_rev=20)
    v = r.rpm()
    print(round(v, 1), "rpm  ->", round(belt_speed_m_s(v, 0.04), 3), "m/s with a 4 cm roller")
