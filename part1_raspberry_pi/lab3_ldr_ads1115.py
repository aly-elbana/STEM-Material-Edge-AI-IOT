"""Lab 3: analog sensor. The Pi can't read voltage, so we add an ADC (ADS1115).
Wiring: ADS1115 VDD -> 3V3, GND -> GND, SDA -> pin 3, SCL -> pin 5 (address 0x48)
        3V3 -> LDR -> midpoint -> 10 kohm -> GND ; midpoint -> A0
Cover the sensor, then shine a light: write down both voltages = your threshold.
"""
import time, board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ads = ADS.ADS1115(board.I2C(), address=0x48)
try:
    ldr = AnalogIn(ads, ADS.P0)      # library v2
except AttributeError:
    ldr = AnalogIn(ads, 0)           # library v3 uses channel numbers

while True:
    print(f"{ldr.voltage:.3f} V   raw={ldr.value}")
    time.sleep(0.5)
