"""Firebase Realtime Database over REST (good if you also build a mobile app).
1. console.firebase.google.com -> Build -> Realtime Database -> create (test mode for
   the prototype only; set rules before sharing!)
2. export FIREBASE_URL=https://<your-db>.firebaseio.com
   (optional) export FIREBASE_AUTH=<database secret or ID token>
"""
import os
import time

import requests

URL = os.environ.get("FIREBASE_URL", "")
AUTH = os.environ.get("FIREBASE_AUTH")


def _params():
    return {"auth": AUTH} if AUTH else {}


def set_latest(path, data):
    """Overwrite one node, e.g. set_latest('team07/belt1/latest', {...})."""
    return requests.put(f"{URL}/{path}.json", json=data, params=_params(), timeout=5).ok


def push(path, data):
    """Append to a list with an auto key, e.g. push('team07/belt1/history', {...})."""
    data = {"ts": time.time(), **data}
    return requests.post(f"{URL}/{path}.json", json=data, params=_params(), timeout=5).ok


if __name__ == "__main__":
    if not URL:
        print("set FIREBASE_URL first")
    else:
        print(set_latest("demo/latest", {"temp": 25}), push("demo/history", {"temp": 25}))
