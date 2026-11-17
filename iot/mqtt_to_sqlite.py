"""Store every MQTT message in a SQLite database (history for analysis / retraining).
    python -m iot.mqtt_to_sqlite "stem/team07/#" --db history.db
Read it later with pandas:  pd.read_sql("SELECT * FROM messages", sqlite3.connect("history.db"))
"""
import argparse
import sqlite3
import time

from common.mqtt_client import EdgeMQTT

p = argparse.ArgumentParser()
p.add_argument("topic")
p.add_argument("--db", default="history.db")
a = p.parse_args()
db = sqlite3.connect(a.db, check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS messages (ts REAL, topic TEXT, payload TEXT)")


def save(topic, payload):
    db.execute("INSERT INTO messages VALUES (?,?,?)", (time.time(), topic, payload))
    db.commit()
    print(topic, payload)


mq = EdgeMQTT("history-logger", outbox="logger_outbox.db")
while not mq.connected:
    time.sleep(0.2)
mq.subscribe(a.topic, save)
while True:
    time.sleep(1)
