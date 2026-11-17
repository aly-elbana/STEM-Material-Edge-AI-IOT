"""HX711 + load cell = weight (grams). Weigh products on a conveyor, a pill box,
a plant pot, food waste...
Wiring: HX711 DT -> GPIO5, SCK -> GPIO6, VCC -> 3V3, GND -> GND.
Calibrate: tare with nothing on it, then put a known weight (e.g. 500 g) and compute
scale = (raw_with_weight - offset) / 500. Save offset and scale.
Simple bit-banged driver (no extra library). Read a few times and average.
"""
import random
import time
from common import SIMULATE


class HX711:
    def __init__(self, dout=5, sck=6, offset=0.0, scale=1.0):
        self.offset, self.scale = offset, scale
        if not SIMULATE:
            from gpiozero import DigitalInputDevice, DigitalOutputDevice
            self.dout = DigitalInputDevice(dout)
            self.sck = DigitalOutputDevice(sck)

    def raw(self):
        if SIMULATE:
            return 84000 + random.gauss(0, 50)
        t0 = time.time()
        while self.dout.value:              # wait until data ready (DOUT low)
            if time.time() - t0 > 1:
                raise TimeoutError("HX711 not ready - check wiring")
        value = 0
        for _ in range(24):
            self.sck.on(); self.sck.off()
            value = (value << 1) | self.dout.value
        self.sck.on(); self.sck.off()        # 25th pulse = channel A, gain 128
        if value & 0x800000:                 # two's complement
            value -= 1 << 24
        return value

    def average(self, n=10):
        return sum(self.raw() for _ in range(n)) / n

    def tare(self, n=15):
        self.offset = self.average(n)

    def grams(self, n=5):
        return (self.average(n) - self.offset) / self.scale


if __name__ == "__main__":
    h = HX711()
    h.tare()
    input("Put a known weight on the scale and press Enter...")
    known = float(input("Weight in grams: "))
    h.scale = (h.average(15) - h.offset) / known
    print("offset =", h.offset, " scale =", h.scale, " -> save these!")
