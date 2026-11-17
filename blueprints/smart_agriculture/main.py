"""Smart irrigation (agriculture / Egypt Grand Challenges: water + food).

Sensors: capacitive soil moisture (ADS1115 A0), BME280, LTR390 (light).
Actuator: 12 V pump / solenoid valve via relay or MOSFET (GPIO26).
Logic: a model predicts "irrigate" from soil + weather features; a SAFETY layer always
limits pump time (max ON seconds, min pause) - never let AI flood the plant.

Baseline first (rule with hysteresis), then train a model on logged data with the
grower's decisions as labels and compare: does the model save water vs the rule?
    python -m blueprints.smart_agriculture.main                       # rule
    python -m blueprints.smart_agriculture.main --model models/irrigation
Calibrate the soil sensor: v_dry = in air, v_wet = in a glass of water (python -m sensors.ads1115).
"""
import argparse
import time

from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from motors.switching import Switch
from sensors import ads1115, bme280, ltr390_uv

p = argparse.ArgumentParser()
p.add_argument("--model")
p.add_argument("--v-dry", type=float, default=2.6)
p.add_argument("--v-wet", type=float, default=1.1)
p.add_argument("--on-below", type=float, default=35, help="% soil moisture: start watering")
p.add_argument("--off-above", type=float, default=55, help="% stop watering (hysteresis)")
p.add_argument("--max-on-s", type=float, default=20)
p.add_argument("--min-pause-s", type=float, default=300)
p.add_argument("--topic", default="stem/team00/farm1/status")
a = p.parse_args()

pump = Switch(pin=26, name="pump")
mq = EdgeMQTT("farm1")
log = CSVLogger("data/irrigation.csv", ["soil_pct", "temp_c", "humidity", "lux", "uv_index",
                                        "pump", "water_s_total"])
model = None
if a.model:
    from ml.tabular.predict_live import LiveModel
    model = LiveModel(a.model)
pumping, on_since, last_off, water_s = False, 0.0, 0.0, 0.0

try:
    while True:
        v, _ = ads1115.read(0)
        x = {"soil_pct": round(ads1115.percent(v, a.v_dry, a.v_wet), 1), **bme280.read(), **ltr390_uv.read()}
        x.pop("pressure_hpa", None)
        if model:
            want = model.predict(x)[0] in ("irrigate", "1", 1, True)
        else:  # hysteresis rule: avoids switching on/off every second
            want = x["soil_pct"] < a.on_below or (pumping and x["soil_pct"] < a.off_above)
        now = time.time()
        if want and not pumping and now - last_off > a.min_pause_s:
            pump.on(); pumping, on_since = True, now
        if pumping and (not want or now - on_since > a.max_on_s):     # safety cut-off
            pump.off(); pumping, last_off = False, now
            water_s += now - on_since
        log.write(**x, pump=int(pumping), water_s_total=round(water_s, 1))
        mq.publish(a.topic, {"ts": round(now, 2), **x, "pump": pumping, "water_s_total": round(water_s, 1)})
        time.sleep(2)
except KeyboardInterrupt:
    pump.off()
    mq.close()
