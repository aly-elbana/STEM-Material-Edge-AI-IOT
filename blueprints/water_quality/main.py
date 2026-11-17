"""Water quality monitor: pH (A0), TDS (A1), turbidity (A2) via ADS1115 + DS18B20 temperature.
Analog probe boards (DFRobot-style) often output up to 3.0-4.5 V -> power them at 3.3 V
if the board allows, or add a voltage divider so A0-A3 never exceed 3.3 V.

Calibration is EVERYTHING here:
  pH: 2 buffer solutions (pH 7 and pH 4) -> save voltages -> linear map (code below).
  TDS: a known calibration solution (e.g. 707 ppm) -> scale factor.
AI: label samples (tap / filtered / bottled / polluted-safe-demo e.g. salt or soil added)
and train a classifier on [ph, tds, turbidity, temp] with ml.tabular.train_tabular.
    python -m blueprints.water_quality.main
"""
import time

from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from sensors import ads1115, ds18b20

PH7_V, PH4_V = 1.50, 2.03            # <- replace with YOUR buffer readings
TDS_K = 1.0                          # <- calibration factor from a known solution


def ph_from_v(v):
    slope = (7.0 - 4.0) / (PH7_V - PH4_V)
    return round(7.0 + slope * (v - PH7_V), 2)


def tds_from_v(v, temp_c):
    comp_v = v / (1.0 + 0.02 * (temp_c - 25.0))           # temperature compensation
    tds = (133.42 * comp_v ** 3 - 255.86 * comp_v ** 2 + 857.39 * comp_v) * 0.5 * TDS_K
    return round(max(0.0, tds), 1)


log = CSVLogger("data/water.csv", ["ph", "tds_ppm", "turbidity_v", "temp_c", "status"])
mq = EdgeMQTT("water1")
while True:
    t = ds18b20.read_c()
    ph = ph_from_v(ads1115.read(0)[0])
    tds = tds_from_v(ads1115.read(1)[0], t)
    turb_v = ads1115.read(2)[0]                            # lower voltage = more turbid
    ok = 6.5 <= ph <= 8.5 and tds < 500 and turb_v > 1.0  # rule baseline - replace with a model
    status = "ok" if ok else "check"
    log.write(ph=ph, tds_ppm=tds, turbidity_v=turb_v, temp_c=t, status=status)
    mq.publish("stem/team00/water1/status", {"ts": round(time.time(), 2), "ph": ph, "tds_ppm": tds,
                                             "turbidity_v": turb_v, "temp_c": t, "status": status})
    print(ph, tds, turb_v, t, status)
    time.sleep(5)
