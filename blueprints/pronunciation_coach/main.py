"""Pronunciation / reading coach (educational pathway) - OFFLINE speech recognition.

The student sees a word, says it; Vosk (offline, runs on the Pi) transcribes it;
we score the similarity to the target and give a tip. Results go to the teacher dashboard.

    sudo apt install libportaudio2 ; pip install vosk sounddevice
    # download a small model from alphacephei.com/vosk/models and unzip, e.g.:
    #   vosk-model-small-en-us-0.15   or   vosk-model-ar-mgb2-0.4 (Arabic, larger)
    python -m blueprints.pronunciation_coach.main --vosk vosk-model-small-en-us-0.15
AI evidence: record N students x M words, label "correct / incorrect" by the teacher,
and report how often the coach agrees with the teacher (accuracy, confusion matrix).
"""
import argparse
import difflib
import json
import random
import time

from common import SIMULATE
from common.mqtt_client import EdgeMQTT
from sensors.microphone import record

WORDS = ["water", "school", "engineer", "beautiful", "temperature", "environment", "vegetable"]

p = argparse.ArgumentParser()
p.add_argument("--vosk", help="path to an unzipped Vosk model folder")
p.add_argument("--seconds", type=float, default=2.5)
p.add_argument("--student", default="student01")
p.add_argument("--pass-score", type=float, default=0.8)
a = p.parse_args()
mq = EdgeMQTT("coach1")
rec = None
if a.vosk and not SIMULATE:
    from vosk import KaldiRecognizer, Model
    vmodel = Model(a.vosk)


def transcribe(audio, rate):
    if not a.vosk or SIMULATE:
        return random.choice([target, target, target[:-1], target + "s", "wada"])
    rec = KaldiRecognizer(vmodel, rate, json.dumps(WORDS + ["[unk]"]))   # limit vocabulary = more accurate
    pcm = (audio * 32767).astype("int16").tobytes()
    rec.AcceptWaveform(pcm)
    return json.loads(rec.FinalResult()).get("text", "")


for target in WORDS:
    input(f"\nSay: '{target}'  (press Enter, then speak)")
    audio, rate = record(a.seconds, 16000)
    t0 = time.perf_counter()
    heard = transcribe(audio, rate)
    score = difflib.SequenceMatcher(None, target, heard.strip()).ratio()
    ms = (time.perf_counter() - t0) * 1000
    ok = score >= a.pass_score
    tip = "Great!" if ok else f"I heard '{heard}'. Listen and try again: {' - '.join(target)}"
    print(f"heard: '{heard}'  score: {score:.0%}  ({ms:.0f} ms)  {tip}")
    mq.publish(f"stem/team00/coach1/{a.student}", {"ts": round(time.time(), 2), "word": target,
                                                   "heard": heard, "score": round(score, 2), "ok": ok})
