"""DC (gear) motor: speed + direction with a driver board.
Use for: conveyor belt, wheels, mixer, fan.
Drivers: TB6612FNG or DRV8833 (efficient, small motors up to ~1-1.5 A),
         L298N (old, wastes ~2 V as heat but common), BTS7960 (big motors, 10 A+).
Wiring (TB6612FNG, channel A):
    PWMA -> GPIO12 (hardware PWM)   AIN1 -> GPIO5   AIN2 -> GPIO6   STBY -> 3V3
    VM -> motor battery +           VCC -> 3V3      GND -> common ground
    AO1/AO2 -> motor
L298N:  ENA -> GPIO12, IN1 -> GPIO5, IN2 -> GPIO6 (remove the ENA jumper).
"""
import time
from common import SIMULATE


class DCMotor:
    def __init__(self, in1=5, in2=6, pwm=12):
        self.speed = 0.0
        self.m = None
        if not SIMULATE:
            from gpiozero import Motor
            self.m = Motor(forward=in1, backward=in2, enable=pwm, pwm=True)

    def run(self, speed):
        """speed -1.0 (full reverse) .. 0 .. +1.0 (full forward)."""
        speed = max(-1.0, min(1.0, speed))
        self.speed = speed
        if self.m is None:
            print(f"[motor] speed {speed:+.2f}")
            return
        if speed > 0:
            self.m.forward(speed)
        elif speed < 0:
            self.m.backward(-speed)
        else:
            self.m.stop()

    def ramp(self, target, seconds=1.0, steps=20):
        """Soft start/stop: protects gears, belts and the power supply."""
        start = self.speed
        for i in range(1, steps + 1):
            self.run(start + (target - start) * i / steps)
            time.sleep(seconds / steps)

    def stop(self):
        self.run(0)


if __name__ == "__main__":
    m = DCMotor()
    m.ramp(0.6, 2)
    time.sleep(3)
    m.ramp(0, 1)
