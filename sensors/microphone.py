"""USB microphone: record a short clip or measure loudness (dB-ish).
sudo apt install libportaudio2 ; pip install sounddevice
"""
import numpy as np
from common import SIMULATE


def record(seconds=1.0, rate=16000):
    if SIMULATE:
        t = np.linspace(0, seconds, int(rate * seconds), endpoint=False)
        return (0.1 * np.sin(2 * np.pi * 440 * t) + 0.01 * np.random.randn(t.size)).astype("float32"), rate
    import sounddevice as sd
    audio = sd.rec(int(seconds * rate), samplerate=rate, channels=1, dtype="float32")
    sd.wait()
    return audio[:, 0], rate


def level_db(audio):
    rms = float(np.sqrt(np.mean(audio ** 2)) + 1e-12)
    return 20 * np.log10(rms)   # relative dBFS (0 = max). Calibrate with a phone app for dB SPL.


if __name__ == "__main__":
    a, r = record()
    print("level:", round(level_db(a), 1), "dBFS")
