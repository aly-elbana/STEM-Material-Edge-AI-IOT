"""One small file per sensor. Each file has read() and runs on its own:
    python -m sensors.bme280
With SIMULATE=1 (default) they return realistic fake values, so every
blueprint runs on a laptop. On the Pi:  export SIMULATE=0
"""
