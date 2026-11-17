"""Smart-classroom logger: one row per second -> room_log.csv
This CSV is the bridge to Part 2: the same idea gives M3 its m3_normal.csv.
Needs: BME280 on I2C (0x76) and a PIR motion sensor on GPIO17 (pin 11).
"""
import csv, os, time, board
from adafruit_bme280 import basic as adafruit_bme280
from gpiozero import MotionSensor

env = adafruit_bme280.Adafruit_BME280_I2C(board.I2C(), address=0x76)
pir = MotionSensor(17)

new_file = not os.path.exists("room_log.csv")
with open("room_log.csv", "a", newline="") as f:
    log = csv.writer(f)
    if new_file:
        log.writerow(["time", "temp_c", "humidity_pct", "motion"])
    while True:
        log.writerow([time.time(), round(env.temperature, 2),
                      round(env.relative_humidity, 2), int(pir.motion_detected)])
        f.flush(); time.sleep(1)
