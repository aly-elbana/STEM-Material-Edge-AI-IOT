"""Lab D: report M3's status with MQTT.

Default = public TEST broker (test.mosquitto.org). Anyone can read it, so
never send real or private data there. For your project use your own broker
(Mosquitto on a Pi, or HiveMQ Cloud) with a username, password and TLS.

To watch the messages, run in another terminal:
  mosquitto_sub -h test.mosquitto.org -t "stem-capstone/+/m3/status" -v
"""
import json, time, random
import paho.mqtt.client as mqtt

BROKER, PORT = "test.mosquitto.org", 1883      # test only, not encrypted
TOPIC = "stem-capstone/team01/m3/status"        # change team01 to your team

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# Real project (encrypted):
#   c.username_pw_set("m3-pi", "your-password")
#   c.tls_set()
#   BROKER, PORT = "your-broker.example.com", 8883
c.connect(BROKER, PORT)
c.loop_start()

for i in range(5):
    msg = {"ts": time.time(), "state": random.choice(["normal", "anomaly"]),
           "temp": round(random.gauss(32, 1), 1)}
    c.publish(TOPIC, json.dumps(msg), qos=1).wait_for_publish()
    print("sent", TOPIC, msg)
    time.sleep(1)

c.loop_stop(); c.disconnect()
