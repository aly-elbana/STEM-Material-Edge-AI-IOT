"""DS18B20 waterproof temperature probe (1-Wire) - water, soil, liquids.
Enable: add  dtoverlay=w1-gpio  to /boot/firmware/config.txt, reboot.
Wiring: DATA -> GPIO4 (pin 7) with a 4.7k pull-up to 3V3; VDD->3V3; GND->GND.
No extra library needed: the kernel exposes it as a file.
"""
import glob
import random
from common import SIMULATE


def read_c():
    if SIMULATE:
        return round(random.gauss(24, 0.2), 2)
    devices = glob.glob("/sys/bus/w1/devices/28-*/temperature")
    if not devices:
        raise RuntimeError("No DS18B20 found - check wiring and dtoverlay=w1-gpio")
    with open(devices[0]) as f:
        return int(f.read().strip()) / 1000.0


if __name__ == "__main__":
    print(read_c(), "C")
