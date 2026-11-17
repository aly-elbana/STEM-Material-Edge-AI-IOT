"""Which motor? + How strong? A calculator for capstone projects.

    python -m motors.motor_sizing                (interactive)

Decision guide (short version):
  * Spin continuously, speed matters, position doesn't  -> DC gear motor + driver
      (conveyor belt, wheels, mixer, fan)
  * Go to an ANGLE and hold it (0-180 deg)              -> Servo
      (reject arm, gate, valve, camera pan/tilt)
  * Move an EXACT distance / angle repeatedly           -> Stepper (+ A4988/TMC2209)
      (indexed conveyor, dispenser, slider, turntable)
  * Very fast, light, efficient spinning                -> BLDC + ESC
      (drone, high-speed fan, impeller)
  * Push / pull / lock in one quick stroke              -> Solenoid (+ MOSFET + diode)
  * Push a heavy load slowly in a straight line         -> Linear actuator
  * Move water / liquid                                 -> 12 V DC pump or peristaltic pump
  * Vibrate to warn a person (wearables, glasses)       -> Coin vibration motor
"""
import math

G = 9.81


def conveyor_torque(load_kg, roller_diameter_m, friction=0.3, incline_deg=0.0,
                    belt_speed_m_s=0.1, safety_factor=2.0, efficiency=0.8):
    """Estimate torque and power for a small belt conveyor.
    friction ~0.3-0.5 for a rubber belt sliding on a flat bed."""
    a = math.radians(incline_deg)
    force_n = load_kg * G * (friction * math.cos(a) + math.sin(a))
    r = roller_diameter_m / 2
    torque_nm = force_n * r * safety_factor
    rpm = belt_speed_m_s / (math.pi * roller_diameter_m) * 60
    power_w = torque_nm * (rpm * 2 * math.pi / 60) / efficiency
    return {"force_N": round(force_n, 2), "torque_Nm": round(torque_nm, 3),
            "torque_kgcm": round(torque_nm / G * 100, 1), "roller_rpm": round(rpm, 1),
            "motor_power_W": round(power_w, 2)}


def servo_torque(arm_length_cm, load_g, safety_factor=2.0):
    """Holding torque needed at the servo shaft, in kg*cm (servo datasheets use kg*cm).
    SG90 ~1.8 kg*cm, MG90S ~2.2, MG996R ~9-11 kg*cm."""
    return round(load_g / 1000 * arm_length_cm * safety_factor, 2)


def wheel_robot(mass_kg, wheel_diameter_m, n_motors=2, slope_deg=5, accel=0.3, rolling=0.05):
    a = math.radians(slope_deg)
    force = mass_kg * (G * (rolling * math.cos(a) + math.sin(a)) + accel)
    torque_each = force * wheel_diameter_m / 2 / n_motors * 1.5
    return {"torque_per_motor_Nm": round(torque_each, 3),
            "torque_per_motor_kgcm": round(torque_each / G * 100, 1)}


if __name__ == "__main__":
    print(__doc__)
    print("Example: 2 kg of bottles on a flat belt, 4 cm roller, 0.1 m/s")
    print(conveyor_torque(2.0, 0.04, belt_speed_m_s=0.1))
    print("Servo pushing a 100 g bottle with a 6 cm arm:", servo_torque(6, 100), "kg*cm")
    print("2-wheel robot, 1.5 kg, 6.5 cm wheels:", wheel_robot(1.5, 0.065))
