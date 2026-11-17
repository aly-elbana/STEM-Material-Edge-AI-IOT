"""MQTT that survives bad Wi-Fi: publish now, or keep it on disk and send later.

    mq = EdgeMQTT(client_id="team07-pi")          # settings from env vars
    mq.publish("stem/team07/m3/status", {"state": "ok", "temp": 31.2})

Environment variables (so passwords never go into your code or GitHub):
    MQTT_HOST   default test.mosquitto.org  (public TEST broker - no private data!)
    MQTT_PORT   default 1883  (8883 = TLS)
    MQTT_USER / MQTT_PASS  for HiveMQ Cloud or your own Mosquitto
    MQTT_TLS=1  to encrypt (needed for HiveMQ Cloud)

Messages that fail to send are stored in outbox.db (SQLite) and re-sent
automatically when the connection comes back. Decide locally. Report globally.
"""
import json
import os
import sqlite3
import threading
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:  # lets the rest of the repo import this file without paho
    mqtt = None


class EdgeMQTT:
    def __init__(self, client_id="capstone-pi", outbox="outbox.db", host=None,
                 port=None, user=None, password=None, tls=None):
        self.host = host or os.environ.get("MQTT_HOST", "test.mosquitto.org")
        self.port = int(port or os.environ.get("MQTT_PORT", "1883"))
        user = user or os.environ.get("MQTT_USER")
        password = password or os.environ.get("MQTT_PASS")
        tls = tls if tls is not None else os.environ.get("MQTT_TLS", "0") == "1"
        self.connected = False
        self._lock = threading.Lock()
        self._db = sqlite3.connect(outbox, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS outbox ("
                         "id INTEGER PRIMARY KEY, topic TEXT, payload TEXT, qos INT)")
        self._db.commit()
        if mqtt is None:
            print("[mqtt] paho-mqtt not installed -> messages go to outbox.db only")
            self.client = None
            return
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        if user:
            self.client.username_pw_set(user, password)
        if tls:
            self.client.tls_set()
        # Last Will: the broker announces "offline" if the Pi dies without saying bye
        self.client.will_set(f"devices/{client_id}/online", "0", qos=1, retain=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        try:
            self.client.connect_async(self.host, self.port, keepalive=30)
            self.client.loop_start()
        except Exception as e:  # no network at start-up is fine
            print("[mqtt] start failed:", e)
        self._client_id = client_id

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self.connected = (reason_code == 0)
        if self.connected:
            print(f"[mqtt] connected to {self.host}:{self.port}")
            client.publish(f"devices/{self._client_id}/online", "1", qos=1, retain=True)
            threading.Thread(target=self.flush, daemon=True).start()
        else:
            print("[mqtt] connect refused:", reason_code)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected = False
        print("[mqtt] disconnected - buffering to disk")

    def publish(self, topic, payload, qos=1, retain=False):
        """payload: dict (sent as JSON) or str. Never blocks your control loop."""
        data = payload if isinstance(payload, str) else json.dumps(payload)
        if self.client is not None and self.connected:
            info = self.client.publish(topic, data, qos=qos, retain=retain)
            if info.rc == 0:
                return True
        with self._lock:
            self._db.execute("INSERT INTO outbox(topic,payload,qos) VALUES(?,?,?)",
                             (topic, data, qos))
            self._db.commit()
        return False

    def flush(self):
        """Send everything that waited while we were offline (oldest first)."""
        with self._lock:
            rows = self._db.execute("SELECT id,topic,payload,qos FROM outbox ORDER BY id").fetchall()
        sent = 0
        for rid, topic, data, qos in rows:
            if not self.connected:
                break
            info = self.client.publish(topic, data, qos=qos)
            if info.rc != 0:
                break
            with self._lock:
                self._db.execute("DELETE FROM outbox WHERE id=?", (rid,))
                self._db.commit()
            sent += 1
        if sent:
            print(f"[mqtt] re-sent {sent} buffered messages")

    def subscribe(self, topic, callback):
        """callback(topic, payload_str) for every message on topic (wildcards ok)."""
        def _on_msg(client, userdata, msg):
            callback(msg.topic, msg.payload.decode(errors="replace"))
        self.client.message_callback_add(topic, _on_msg)
        self.client.subscribe(topic, qos=1)

    def pending(self):
        return self._db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]

    def close(self):
        if self.client is not None:
            self.client.publish(f"devices/{self._client_id}/online", "0", qos=1, retain=True)
            time.sleep(0.2)
            self.client.loop_stop()
            self.client.disconnect()
