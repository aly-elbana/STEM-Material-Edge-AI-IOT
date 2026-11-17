"""Print every message under a topic (wildcards: + = one level, # = everything below).
    python -m iot.subscribe "stem/team07/#"
"""
import sys
import time

from common.mqtt_client import EdgeMQTT

topic = sys.argv[1] if len(sys.argv) > 1 else "stem/#"
mq = EdgeMQTT("viewer", outbox="viewer_outbox.db")
while not mq.connected:
    time.sleep(0.2)
mq.subscribe(topic, lambda t, p: print(time.strftime("%H:%M:%S"), t, p))
while True:
    time.sleep(1)
