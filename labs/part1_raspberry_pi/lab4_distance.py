"""Lab 4: 5 V sensor - HC-SR04. PROTECT the echo input!
Wiring: VCC -> 5V (pin 2), GND -> pin 6, TRIG -> GPIO23 (pin 16)
        ECHO -> 330 ohm -> GPIO24 (pin 18), and GPIO24 -> 470 ohm -> GND
        Vout = 5 x 470 / (330 + 470) = 2.94 V  -> safe for 3.3 V GPIO
"""
import time
from gpiozero import DistanceSensor

s = DistanceSensor(echo=24, trigger=23)
while True:
    print(round(s.distance * 100, 1), "cm")   # check with a ruler!
    time.sleep(0.5)
