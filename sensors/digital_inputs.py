"""On/off sensors on GPIO: button, PIR motion, IR break-beam (object counter),
reed switch (door), limit switch, vibration switch, rain sensor DO pin.
All are 3.3 V safe when powered from 3V3 (check 5 V modules' output first!).
"""
from common import SIMULATE


def object_counter(pin=17, on_object=None):
    """IR break-beam or IR obstacle module: counts objects passing on a conveyor.
    on_object() is called once per object (on the falling edge)."""
    if SIMULATE:
        print("[sim] counter ready (no hardware)")
        return None
    from gpiozero import DigitalInputDevice
    beam = DigitalInputDevice(pin, pull_up=True, bounce_time=0.01)
    if on_object:
        beam.when_deactivated = on_object   # beam broken -> input goes low
    return beam


def motion(pin=17):
    from gpiozero import MotionSensor
    return MotionSensor(pin)


def button(pin=5, on_press=None):
    from gpiozero import Button
    b = Button(pin, bounce_time=0.05)
    if on_press:
        b.when_pressed = on_press
    return b


if __name__ == "__main__":
    import time
    n = {"count": 0}

    def hit():
        n["count"] += 1
        print("object", n["count"])

    object_counter(on_object=hit)
    time.sleep(30)
