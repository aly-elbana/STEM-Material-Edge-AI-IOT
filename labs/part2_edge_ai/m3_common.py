"""Shared helpers for the M3 labs.

M3 is a FICTIONAL motor in a juice factory, used as a running example.
SIMULATE = True means: no Raspberry Pi or sensors needed, readings are generated.
"""
import random

FEATURES = ["temp", "vibration", "current"]


def fake_reading(fault=None):
    """One reading of M3: temperature (C), vibration (g), current (A)."""
    temp = random.gauss(32.0, 0.8)
    vib = random.gauss(0.60, 0.05)
    cur = random.gauss(4.20, 0.15)
    if fault == "bearing":      # worn bearing -> strong vibration
        vib += random.uniform(0.25, 0.45)
    elif fault == "overheat":   # blocked cooling -> hot motor
        temp += random.uniform(3.5, 6.0)
    elif fault == "overload":   # jammed belt -> high current
        cur += random.uniform(0.6, 1.2)
        temp += random.uniform(0.5, 1.5)
    return [round(temp, 2), round(vib, 3), round(cur, 2)]
