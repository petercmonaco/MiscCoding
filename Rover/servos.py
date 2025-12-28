from asyncio import sleep as async_sleep
from adafruit_servokit import ServoKit
from imu import current_heading
kit = ServoKit(channels=8)

kit.servo[0].set_pulse_width_range(450, 2550)
kit.servo[0].angle = 90

async def _test_sweep():
    angle = 0
    direction = 1
    while True:
        kit.servo[0].angle = angle
        angle += direction * 5
        if angle >= 180 or angle <= 0:
            direction *= -1
        await async_sleep(0.1)

pause_tracking = False

def handle_servo_cmd(cmd):
    cmd_words = cmd.split()
    if cmd_words[0] != 'servo':
        return (False, 'Not for me')
    try:
        snum = int(cmd_words[1])
        if cmd_words[2] == 'track':
            enable_tracking()
            return (True, None)
        angle = int(cmd_words[2])
        set_servo(snum, angle)
        return (True, None)
    except (ValueError, IndexError):
        return (True, 'Malformed servo command')

def set_servo(snum, angle):
    global pause_tracking
    pause_tracking = True
    kit.servo[snum].angle = angle

def enable_tracking():
    global pause_tracking
    pause_tracking = False

def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

def point_lidar_to_calibrated_heading(h):
    # To point to 270, send signal for 166
    # To point to 360, send signal 83
    # To point to 90, send signal 0
    if h < 180:
        h += 360
    h = clamp(h, 270, 450)
    desired_angle = int((450 - h) * 166/180)
    kit.servo[0].angle = desired_angle

async def do_point_lidar():
    global pause_tracking
    while True:
        if not pause_tracking:
            h = current_heading()
            point_lidar_to_calibrated_heading(360-h)
        await async_sleep(0.1)
        