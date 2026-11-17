"""TEMPLATE - copy this folder for ANY capstone idea.

    cp -r blueprints/template blueprints/my_project
    python -m blueprints.my_project.main

The four blocks below are the whole architecture (Decide locally. Report globally.):
  SENSE  -> read sensors / camera
  THINK  -> features + model (or rules first, model later)
  ACT    -> local output immediately (buzzer, servo, relay, screen, voice)
  REPORT -> MQTT to the cloud/dashboard, never blocking the loop
Everything you need for the capstone evidence is logged automatically:
  data/<project>.csv        every reading + decision  (dataset + logbook)
  response_times.csv        input->output latency      (requirement: response time)
"""
import random
import time

from common import SIMULATE
from common.alerts import LocalAlarm
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog

TEAM, DEVICE = "team00", "device1"
TOPIC = f"stem/{TEAM}/{DEVICE}/status"
PERIOD_S = 0.5          # how often the loop runs
REPORT_EVERY_S = 5      # how often we send to the cloud


def sense():
    """Replace with real sensors, e.g.  from sensors import bme280; return bme280.read()"""
    return {"value": round(random.gauss(50, 5), 2)}


def think(x):
    """Start with a RULE (baseline). Then train a model and compare: does AI beat the rule?
    e.g.  from ml.tabular.predict_live import LiveModel; label, ms = MODEL.predict(x)"""
    return "alert" if x["value"] > 60 else "normal"


def act(decision, alarm):
    alarm.set(decision == "alert")


def main():
    print("SIMULATE =", SIMULATE)
    alarm = LocalAlarm(pin=27)
    mq = EdgeMQTT(client_id=f"{TEAM}-{DEVICE}")
    log = CSVLogger(f"data/{DEVICE}.csv", ["value", "decision", "latency_ms"])
    lat = LatencyLog()
    last_report = 0
    try:
        while True:
            t0 = lat.start()
            x = sense()
            decision = think(x)
            act(decision, alarm)
            ms = lat.stop(t0, decision)
            log.write(**x, decision=decision, latency_ms=round(ms, 2))
            if time.time() - last_report > REPORT_EVERY_S or decision != "normal":
                mq.publish(TOPIC, {"ts": round(time.time(), 2), "decision": decision, **x})
                last_report = time.time()
            time.sleep(PERIOD_S)
    except KeyboardInterrupt:
        print("\n", lat.summary())
        mq.close()


if __name__ == "__main__":
    main()
