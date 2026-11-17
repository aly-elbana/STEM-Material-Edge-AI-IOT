"""Get the I2C bus once (pins 3 = SDA, 5 = SCL). Enable I2C first:
    sudo raspi-config -> Interface Options -> I2C -> Enable
Check what is connected:  i2cdetect -y 1
"""
_bus = None


def get_i2c():
    global _bus
    if _bus is None:
        import board
        _bus = board.I2C()
    return _bus
