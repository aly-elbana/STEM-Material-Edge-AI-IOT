"""Stepper motor: exact POSITION without a sensor (count steps).
Use for: indexed conveyor (move exactly one slot), dispensers (pills, seeds, food),
camera slider, rotating platform, 3D-printer style axes.
Drivers: A4988 / DRV8825 (cheap), TMC2209 (quiet). NEMA17 = common motor.
Wiring (A4988): STEP -> GPIO20, DIR -> GPIO21, EN -> GPIO16 (low = enabled),
VMOT -> 8-24 V supply (+100 uF capacitor!), VDD -> 3V3, GND common.
Set the driver's current limit with its small potentiometer BEFORE running.
28BYJ-48 + ULN2003 (tiny, cheap, slow) also works: see half_step_28byj48().
Full-step NEMA17 = 200 steps/rev (1.8 deg). With 1/16 microstepping = 3200 steps/rev.
"""
import time
from common import SIMULATE


class Stepper:
    def __init__(self, step=20, direction=21, enable=16, steps_per_rev=200):
        self.spr = steps_per_rev
        self.pos = 0
        if not SIMULATE:
            from gpiozero import DigitalOutputDevice
            self.step_pin = DigitalOutputDevice(step)
            self.dir_pin = DigitalOutputDevice(direction)
            self.en = DigitalOutputDevice(enable, active_high=False, initial_value=True)

    def move(self, steps, rpm=60):
        """Positive = one direction, negative = the other."""
        delay = 60.0 / (rpm * self.spr) / 2
        if SIMULATE:
            print(f"[stepper] {steps:+d} steps at {rpm} rpm")
            self.pos += steps
            return
        self.dir_pin.value = steps > 0
        for _ in range(abs(steps)):
            self.step_pin.on(); time.sleep(delay)
            self.step_pin.off(); time.sleep(delay)
        self.pos += steps

    def rotate_deg(self, degrees, rpm=60):
        self.move(int(round(degrees / 360.0 * self.spr)), rpm)

    def release(self):
        if not SIMULATE:
            self.en.off()   # motor goes limp, stops heating


def half_step_28byj48(pins=(17, 18, 27, 22), steps=4096, delay=0.0015):
    """28BYJ-48 via ULN2003: 4096 half-steps = 1 revolution."""
    seq = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0],
           [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]]
    if SIMULATE:
        print(f"[28byj48] {steps} half-steps")
        return
    from gpiozero import DigitalOutputDevice
    coils = [DigitalOutputDevice(p) for p in pins]
    for i in range(abs(steps)):
        pattern = seq[i % 8] if steps > 0 else seq[-(i % 8) - 1]
        for c, v in zip(coils, pattern):
            c.value = v
        time.sleep(delay)
    for c in coils:
        c.off()


if __name__ == "__main__":
    s = Stepper()
    s.rotate_deg(90)
    s.rotate_deg(-90)
