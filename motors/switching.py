"""ON/OFF loads: pump, solenoid (lock / pusher), lamp, fan, heater, valve, buzzer.
- Relay module: any voltage, slow switching, isolated. Many modules are ACTIVE-LOW.
- Logic-level MOSFET module (IRLZ44N, AO3400): DC loads, fast, PWM-able (fan speed).
- ALWAYS a flyback diode (1N4007) across motors / solenoids / pumps (relay modules
  usually have one for the coil, NOT for your load).
- Mains 220 V: only with a teacher, inside a closed box, or use a ready smart plug.
"""
from common import SIMULATE


class Switch:
    def __init__(self, pin=26, active_low=True, name="load"):
        self.name = name
        self.dev = None
        if not SIMULATE:
            from gpiozero import OutputDevice
            self.dev = OutputDevice(pin, active_high=not active_low, initial_value=False)

    def on(self):
        print(f"[{self.name}] ON") if self.dev is None else self.dev.on()

    def off(self):
        print(f"[{self.name}] off") if self.dev is None else self.dev.off()


class PWMLoad:
    """Fan / LED strip / vibration motor speed via MOSFET (0..1)."""

    def __init__(self, pin=13, frequency=1000):
        self.dev = None
        if not SIMULATE:
            from gpiozero import PWMOutputDevice
            self.dev = PWMOutputDevice(pin, frequency=frequency)

    def set(self, level):
        level = max(0.0, min(1.0, level))
        print(f"[pwm] {level:.2f}") if self.dev is None else setattr(self.dev, "value", level)


if __name__ == "__main__":
    import time
    pump = Switch(name="pump")
    pump.on(); time.sleep(2); pump.off()
