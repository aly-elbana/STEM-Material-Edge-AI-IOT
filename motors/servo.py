"""Servo motors: move to an ANGLE (0-180 deg). Use for: reject arm / pusher on a
conveyor, gates, valves, pan-tilt camera, robotic fingers.
Continuous-rotation servos (MG996R-360, FS90R) spin instead: value = speed.

Option A - gpiozero on one GPIO (fine for 1-2 servos; may jitter a little):
    signal -> GPIO18,  V+ -> separate 5-6 V supply (NOT the Pi's 5 V for big servos),
    GND -> common ground.
Option B - PCA9685 16-channel board (I2C 0x40): jitter-free, many servos.
    pip install adafruit-circuitpython-servokit
"""
import time
from common import SIMULATE


class Servo:
    def __init__(self, pin=18, channel=None, min_pulse=0.0005, max_pulse=0.0025):
        self.kind = "sim"
        if SIMULATE:
            return
        if channel is not None:
            from adafruit_servokit import ServoKit
            self.kit = ServoKit(channels=16)
            self.ch = channel
            self.kind = "pca9685"
        else:
            from gpiozero import AngularServo
            self.s = AngularServo(pin, min_angle=0, max_angle=180,
                                  min_pulse_width=min_pulse, max_pulse_width=max_pulse)
            self.kind = "gpio"

    def angle(self, deg):
        deg = max(0, min(180, deg))
        if self.kind == "pca9685":
            self.kit.servo[self.ch].angle = deg
        elif self.kind == "gpio":
            self.s.angle = deg
        else:
            print(f"[servo] -> {deg} deg")

    def push(self, out=110, home=20, hold=0.25):
        """Reject a bad item: swing out, hold, come back."""
        self.angle(out)
        time.sleep(hold)
        self.angle(home)


if __name__ == "__main__":
    s = Servo()
    for a in (0, 90, 180, 90):
        s.angle(a)
        time.sleep(0.7)
