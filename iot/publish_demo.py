"""Publish fake readings every second (test your broker / dashboard).
    python -m iot.publish_demo --topic stem/team07/demo/status
Then pull the network cable / turn Wi-Fi off and on: messages are buffered and re-sent.
"""
import argparse
import random
import time

from common.mqtt_client import EdgeMQTT

p = argparse.ArgumentParser()
p.add_argument("--topic", default="stem/team07/demo/status")
p.add_argument("--n", type=int, default=0, help="0 = forever")
a = p.parse_args()
mq = EdgeMQTT("demo-publisher")
i = 0
while a.n == 0 or i < a.n:
    msg = {"ts": round(time.time(), 2), "temp": round(random.gauss(30, 1), 2),
           "state": random.choice(["normal"] * 9 + ["anomaly"])}
    ok = mq.publish(a.topic, msg)
    print("sent" if ok else "buffered", msg, "| waiting:", mq.pending())
    i += 1
    time.sleep(1)
mq.close()
