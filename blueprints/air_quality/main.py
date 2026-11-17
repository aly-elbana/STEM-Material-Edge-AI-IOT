"""Air quality station: PM2.5 (PMS5003) + eCO2/TVOC (SGP30) + temp/humidity (BME280).
Computes the US EPA AQI for PM2.5, predicts the next 15 minutes with a simple trend
model, and runs a fan/purifier BEFORE the air gets bad (that's the "AI" story:
predict, don't just react). Evaluate the forecast error (MAE) on held-out days.
    python -m blueprints.air_quality.main
"""
import collections
import time

import numpy as np

from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from motors.switching import Switch
from sensors import bme280, pms5003_dust, sgp30_air

# US EPA PM2.5 (24-h) breakpoints, 2024 update: (C_low, C_high, I_low, I_high)
BP = [(0.0, 9.0, 0, 50), (9.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), (55.5, 125.4, 151, 200),
      (125.5, 225.4, 201, 300), (225.5, 325.4, 301, 500)]


def aqi_pm25(c):
    c = round(c, 1)
    for cl, ch, il, ih in BP:
        if cl <= c <= ch:
            return round((ih - il) / (ch - cl) * (c - cl) + il)
    return 500


fan, mq = Switch(26, name="purifier"), EdgeMQTT("air1")
log = CSVLogger("data/air.csv", ["pm25", "aqi", "eco2_ppm", "tvoc_ppb", "temp_c", "humidity", "pm25_pred_15min"])
hist = collections.deque(maxlen=90)          # last 90 readings (every 10 s = 15 min)
while True:
    pm, gas, env = pms5003_dust.read(), sgp30_air.read(), bme280.read()
    hist.append(pm["pm25"])
    pred = pm["pm25"]
    if len(hist) >= 10:                       # linear trend -> value in 15 minutes
        y = np.array(hist, float)
        slope, icpt = np.polyfit(np.arange(len(y)), y, 1)
        pred = max(0.0, icpt + slope * (len(y) - 1 + 90))
    aqi = aqi_pm25(pm["pm25"])
    (fan.on if aqi > 100 or aqi_pm25(pred) > 100 else fan.off)()
    row = {"pm25": pm["pm25"], "aqi": aqi, **gas, "temp_c": env["temp_c"],
           "humidity": env["humidity"], "pm25_pred_15min": round(pred, 1)}
    log.write(**row)
    mq.publish("stem/team00/air1/status", {"ts": round(time.time(), 2), **row})
    time.sleep(10)
