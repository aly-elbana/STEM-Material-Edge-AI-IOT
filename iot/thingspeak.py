"""ThingSpeak: free cloud charts with zero web code (good for a first dashboard).
1. thingspeak.com -> New Channel -> enable Field 1..8 (e.g. temp, humidity, count)
2. API Keys -> copy the WRITE key -> export THINGSPEAK_KEY=...
Free accounts accept one update every ~15 s - send averages, not every reading.
"""
import os

import requests


def send(**fields):
    """send(field1=24.5, field2=51) -> True if accepted."""
    key = os.environ.get("THINGSPEAK_KEY")
    if not key:
        print("[thingspeak] set THINGSPEAK_KEY", fields)
        return False
    try:
        r = requests.get("https://api.thingspeak.com/update",
                         params={"api_key": key, **fields}, timeout=5)
        return r.ok and r.text.strip() != "0"
    except requests.RequestException as e:
        print("[thingspeak]", e)
        return False


if __name__ == "__main__":
    print(send(field1=25.1, field2=48))
