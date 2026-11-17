"""Shared helpers used by every blueprint.

Import from the repo root, for example:
    from common.timing import LatencyLog
    from common.mqtt_client import EdgeMQTT
Run scripts from the repo root:  python -m blueprints.01_conveyor_qc.main
or add the repo root to PYTHONPATH.
"""
import os

# One switch for the whole repo. SIMULATE=1 (default on a laptop) means:
# no Raspberry Pi, no sensors, no camera needed - readings are generated.
# On the Pi with real hardware:  export SIMULATE=0
SIMULATE = os.environ.get("SIMULATE", "1") == "1"
