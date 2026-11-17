"""PMS5003 particulate sensor (PM1.0 / PM2.5 / PM10) over UART.
Wiring: VCC -> 5V, GND -> GND, TX(sensor) -> GPIO15 RXD (pin 10). Its logic is 3.3 V.
Enable serial port (no login shell): sudo raspi-config -> Interface -> Serial.
pip install adafruit-circuitpython-pm25 pyserial
"""
import random
from common import SIMULATE

_pm = None


def read():
    global _pm
    if SIMULATE:
        return {"pm1": random.randint(5, 15), "pm25": random.randint(8, 40), "pm10": random.randint(15, 60)}
    if _pm is None:
        import serial
        from adafruit_pm25.uart import PM25_UART
        uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.95)
        _pm = PM25_UART(uart, None)
    d = _pm.read()
    return {"pm1": d["pm10 env"], "pm25": d["pm25 env"], "pm10": d["pm100 env"]}


if __name__ == "__main__":
    print(read())
