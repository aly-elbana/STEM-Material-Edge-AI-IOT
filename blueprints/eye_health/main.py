"""Eye health assistant for screen / study time (medical pathway, NO diagnosis).

Measures what is known to strain eyes and reminds the user:
  * too close to the screen        -> camera face-distance or VL53L0X laser
  * too long without a break       -> 20-20-20 rule (every 20 min, look 20 ft/6 m away, 20 s)
  * blinking too little            -> camera blink rate (normal ~15-20/min; drops on screens)
  * bad room light for reading     -> LTR390 lux
  * strong blue share in the light -> AS7341 spectral bands (relative indicator)
  * UV outdoors                    -> LTR390 UV index (sunglasses reminder at UVI >= 3)
SAFETY: this device only MEASURES light. Never shine UV, IR or bright light into eyes.
It gives habits reminders, not medical advice.

    python -m blueprints.eye_health.main                 # simulation
    SIMULATE=0 python -m blueprints.eye_health.main --camera --tof
"""
import argparse
import random
import time

from common import SIMULATE
from common.alerts import LocalAlarm, say
from common.datalog import CSVLogger
from common.mqtt_client import EdgeMQTT
from common.timing import LatencyLog
from sensors import as7341_spectral, ltr390_uv, vl53l0x

p = argparse.ArgumentParser()
p.add_argument("--camera", action="store_true", help="blink rate + distance from camera (MediaPipe)")
p.add_argument("--tof", action="store_true", help="screen distance from VL53L0X")
p.add_argument("--min-distance", type=float, default=50, help="cm")
p.add_argument("--break-every-min", type=float, default=20)
p.add_argument("--min-blinks", type=float, default=10, help="per minute")
p.add_argument("--min-lux", type=float, default=300)
p.add_argument("--topic", default="stem/team00/eye1/status")
p.add_argument("--lang", default="en", help="voice: en or ar")
a = p.parse_args()

MSG = {
    "en": {"close": "You are too close to the screen", "break": "Time for a break. Look far away for twenty seconds",
           "blink": "Remember to blink", "dark": "The light is too low for reading",
           "uv": "High UV. Wear sunglasses", "blue": "Strong blue light. Try night mode"},
    "ar": {"close": "انت قريب جدا من الشاشة", "break": "خد استراحة وبص بعيد عشرين ثانية",
           "blink": "افتكر ترمش", "dark": "الاضاءة ضعيفة للقراية",
           "uv": "الأشعة فوق البنفسجية عالية البس نضارة شمس", "blue": "الضوء الأزرق عالي شغل الوضع الليلي"},
}[a.lang]

alarm = LocalAlarm(pin=27)
mq = EdgeMQTT("eye1")
lat = LatencyLog("eye_latency.csv")
log = CSVLogger("data/eye_health.csv", ["distance_cm", "blinks_per_min", "lux", "uv_index",
                                        "blue_ratio", "screen_min", "alerts"])
blink = None
cam = None
if a.camera and not SIMULATE:
    from common.camera import Camera
    from blueprints.eye_health.blink import BlinkMeter
    cam, blink = Camera((640, 480)), BlinkMeter()

session_start = time.time()
too_close_since = None
last_said = {}


def remind(key, cooldown=60):
    if time.time() - last_said.get(key, 0) > cooldown:
        last_said[key] = time.time()
        alarm.beep(1)
        say(MSG[key], a.lang)


try:
    while True:
        t0 = lat.start()
        x = {"distance_cm": None, "blinks_per_min": None}
        if blink:
            x.update({k: v for k, v in blink.update(cam.read()).items()
                      if k in ("distance_cm", "blinks_per_min")})
        elif SIMULATE:
            x["blinks_per_min"] = round(random.gauss(13, 4), 1)
        if a.tof or SIMULATE:
            x["distance_cm"] = vl53l0x.read_cm()
        light = ltr390_uv.read()
        spec = as7341_spectral.read()
        x.update(lux=light["lux"], uv_index=light["uv_index"],
                 blue_ratio=round(as7341_spectral.blue_ratio(spec), 3),
                 screen_min=round((time.time() - session_start) / 60, 1))

        alerts = []
        d = x["distance_cm"]
        if d is not None and d < a.min_distance:
            too_close_since = too_close_since or time.time()
            if time.time() - too_close_since > 10:          # 10 s, not every lean-in
                alerts.append("close")
        else:
            too_close_since = None
        if x["screen_min"] >= a.break_every_min:
            alerts.append("break")
            session_start = time.time()                     # restart the 20-min timer
        if x["blinks_per_min"] is not None and x["blinks_per_min"] < a.min_blinks:
            alerts.append("blink")
        if x["lux"] < a.min_lux:
            alerts.append("dark")
        if x["uv_index"] >= 3:
            alerts.append("uv")
        if x["blue_ratio"] > 0.5 and time.localtime().tm_hour >= 21:
            alerts.append("blue")
        for k in alerts:
            remind(k, cooldown=20 if SIMULATE else 120)
        ms = lat.stop(t0, ",".join(alerts))
        log.write(**x, alerts="|".join(alerts))
        mq.publish(a.topic, {"ts": round(time.time(), 2), **x, "alerts": alerts, "loop_ms": round(ms, 1)})
        time.sleep(1.0)
except KeyboardInterrupt:
    print("\n", lat.summary())
    mq.close()
