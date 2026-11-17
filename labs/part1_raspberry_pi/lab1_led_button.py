"""Lab 1: proof of life. Button -> LED.
Wiring: GPIO27 (pin 13) -> 330 ohm -> LED -> GND (pin 6)
        Button between GPIO5 (pin 29) and GND (internal pull-up)
"""
from gpiozero import LED, Button
from signal import pause

led = LED(27)       # GPIO27 = pin 13
button = Button(5)  # internal pull-up

button.when_pressed = led.on
button.when_released = led.off

pause()             # keep the program alive (Ctrl+C to stop)
