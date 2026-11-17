# IoT + cloud: send results, show them, alert people

```
 Pi (decides)  --MQTT-->  Broker  --> dashboard (browser)  /  database  /  phone alert
```
| Need | Easiest option | File |
|---|---|---|
| Publish from the Pi (with offline buffer) | `common/mqtt_client.py` | `iot/publish_demo.py` |
| Watch messages | `iot/subscribe.py` or MQTT Explorer app | `iot/subscribe.py` |
| Broker in the classroom (no internet) | Mosquitto on the Pi | `iot/mosquitto_setup.md` |
| Free cloud broker with TLS | HiveMQ Cloud Serverless (free tier) | env vars in `common/mqtt_client.py` |
| Live dashboard | `iot/dashboard/app.py` (Flask) or Node-RED | `iot/dashboard/` |
| Charts with zero code | ThingSpeak | `iot/thingspeak.py` |
| History in a database | SQLite logger | `iot/mqtt_to_sqlite.py` |
| Phone alert | Telegram bot | `common/alerts.py` |
| Realtime database / app backend | Firebase Realtime Database (REST) | `iot/firebase_rest.py` |

## Topic naming (use it everywhere)
`stem/<team>/<device>/<what>`  e.g. `stem/team07/belt1/status`, `stem/team07/belt1/count`.
Payload = small JSON **with a timestamp**: `{"ts": 1731840000.1, "state": "anomaly", "score": 0.91}`.
Send **results**, not raw video / private data.

## Node-RED (drag-and-drop dashboard)
```bash
bash <(curl -sL https://github.com/node-red/linux-installers/releases/latest/download/update-nodejs-and-nodered-deb)
sudo systemctl enable --now nodered
```
Open http://<pi-ip>:1880 -> Manage palette -> install `@flowfuse/node-red-dashboard`.
Flow: **mqtt in** (topic `stem/team07/#`) -> **json** -> **ui-gauge / ui-chart**. Dashboard at `/dashboard`.
