#!/usr/bin/env bash
# One-time setup on a fresh Raspberry Pi OS (64-bit, Bookworm or newer).
#   bash tools/setup_pi.sh
set -e
sudo apt update
sudo apt install -y python3-venv python3-picamera2 python3-opencv i2c-tools espeak-ng \
                    libportaudio2 mosquitto-clients git
sudo raspi-config nonint do_i2c 0      # enable I2C
sudo raspi-config nonint do_spi 0      # enable SPI
python3 -m venv --system-site-packages ~/capstone-env
source ~/capstone-env/bin/activate
pip install --upgrade pip
pip install -r requirements-pi.txt
echo "Done. Next time:  source ~/capstone-env/bin/activate"
echo "Check sensors:     i2cdetect -y 1"
