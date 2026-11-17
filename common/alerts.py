"""Alerts for people: local (buzzer / LED / voice) and remote (Telegram).

Local alerts must never wait for the internet.

Telegram setup (5 minutes, free):
  1. In Telegram talk to @BotFather -> /newbot -> copy the TOKEN
  2. Send any message to your new bot, then open
     https://api.telegram.org/bot<TOKEN>/getUpdates and copy "chat":{"id": ...}
  3. export TELEGRAM_TOKEN=...   export TELEGRAM_CHAT_ID=...
"""
import os
import shutil
import subprocess
import threading

from common import SIMULATE


class LocalAlarm:
    """Buzzer or LED on a GPIO pin. In SIMULATE mode it just prints."""

    def __init__(self, pin=27):
        self.on_state = False
        self.dev = None
        if not SIMULATE:
            from gpiozero import Buzzer
            self.dev = Buzzer(pin)

    def set(self, on):
        on = bool(on)
        if on != self.on_state:
            print("[alarm] ON" if on else "[alarm] off")
        self.on_state = on
        if self.dev is not None:
            self.dev.value = on

    def beep(self, times=2, on_time=0.1, off_time=0.1):
        if self.dev is not None:
            self.dev.beep(on_time=on_time, off_time=off_time, n=times, background=True)
        else:
            print("[alarm] beep x", times)


def say(text, lang="en"):
    """Offline text-to-speech with espeak-ng (sudo apt install espeak-ng).
    Arabic: lang="ar". Runs in the background so the loop keeps going."""
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if exe is None:
        print("[say]", text)
        return
    threading.Thread(target=subprocess.run,
                     args=([exe, "-v", lang, "-s", "160", text],),
                     kwargs={"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL},
                     daemon=True).start()


def telegram(text):
    """Send a Telegram message. Returns True if sent. Never raises."""
    token = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("[telegram not configured]", text)
        return False
    try:
        import requests
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          data={"chat_id": chat, "text": text}, timeout=5)
        return r.ok
    except Exception as e:
        print("[telegram] failed:", e)
        return False
