"""A tiny live dashboard: subscribes to MQTT and shows the latest values + a chart
in the browser. Runs on the Pi or a laptop.

    pip install flask paho-mqtt
    python -m iot.dashboard.app --topic "stem/team07/#"
    open http://<pi-ip>:5000
Any numeric field in your JSON payloads gets a card and a line on the chart.
"""
import argparse
import collections
import json
import time

from flask import Flask, jsonify, render_template

from common.mqtt_client import EdgeMQTT

p = argparse.ArgumentParser()
p.add_argument("--topic", default="stem/#")
p.add_argument("--port", type=int, default=5000)
a = p.parse_args()

app = Flask(__name__)
latest = {}
history = collections.deque(maxlen=300)


def on_msg(topic, payload):
    try:
        data = json.loads(payload)
    except ValueError:
        data = {"value": payload}
    if not isinstance(data, dict):
        data = {"value": data}
    data["_topic"], data["_time"] = topic, time.strftime("%H:%M:%S")
    latest[topic] = data
    nums = {f"{topic.split('/')[-2] if topic.count('/') > 1 else topic}.{k}": v
            for k, v in data.items() if isinstance(v, (int, float)) and k != "ts"}
    history.append({"t": data["_time"], **nums})


@app.route("/")
def index():
    return render_template("index.html", topic=a.topic)


@app.route("/data")
def data():
    return jsonify(latest=latest, history=list(history))


if __name__ == "__main__":
    mq = EdgeMQTT("dashboard", outbox="dashboard_outbox.db")
    while not mq.connected:
        time.sleep(0.2)
    mq.subscribe(a.topic, on_msg)
    app.run(host="0.0.0.0", port=a.port)
