"""Lab 2: digital sensor over I2C - BME280 (temperature, humidity, pressure).
Wiring: VIN -> 3V3 (pin 1), SDA -> pin 3, SCL -> pin 5, GND -> pin 6
First enable I2C:  sudo raspi-config -> Interface Options -> I2C
Check:  i2cdetect -y 1   -> you should see 76
"""
import board
from adafruit_bme280 import basic as adafruit_bme280

i2c = board.I2C()
env = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

print(round(env.temperature, 1), "C")
print(round(env.relative_humidity, 1), "%")
print(round(env.pressure, 1), "hPa")
