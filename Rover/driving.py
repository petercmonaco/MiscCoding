from asyncio import sleep as async_sleep
from adafruit_motorkit import MotorKit
from imu import current_heading
from utils import HeadingStopper

# Motor Stuff
motorkit = MotorKit() # Implicit args: address=0x60, i2c=board.I2C()

def _set_throttles(thr1, thr2):
    motorkit.motor1.throttle = thr1
    motorkit.motor2.throttle = thr2
    return (True, None) # Success; returning this tuple is helpful for next layer up

WHEEL_SEP = 98 # mm

stop_condition = None

def handle_driving_cmd(cmd):
    global stop_condition
    cmd_words = cmd.split()
    if cmd_words[0] not in ['drive', 'stop', 'rotate', 'arc']:
        return (False, 'Not for me')
    if cmd == 'stop':
        return _set_throttles(0, 0)
    if cmd == 'drive':
        return _set_throttles(1, 1)
    if cmd == 'rotate left':
        return _set_throttles(-1, 1)
    if cmd == 'rotate right':
        return _set_throttles(1, -1)
    if cmd_words[0] == 'arc':
        try:
            arc_dir = cmd_words[1]
            arc_radius = int(cmd_words[2])
            arc_stop_at_hdg = int(cmd_words[3])
            inner_wheel_speed = (arc_radius - (WHEEL_SEP / 2)) / (arc_radius + (WHEEL_SEP / 2))
            if arc_dir == 'left':
                _set_throttles(inner_wheel_speed, 1)
            elif arc_dir == 'right':
                _set_throttles(1, inner_wheel_speed)
            else:
                return (True, 'Invalid arc direction')
            stop_condition = HeadingStopper(current_heading(), arc_dir, arc_stop_at_hdg)
            return (True, None)
        except ValueError:
            return (True, 'Malformed arc cmd')
    else:
        return (True, 'Malformed driving command')

def driving_stop():
    _set_throttles(0, 0)


async def handle_driving():
    global stop_condition
    while True:
        await async_sleep(0.01)
        if stop_condition is not None:
            if stop_condition.should_stop(current_heading()):
                driving_stop()
                stop_condition = None