from adafruit_motorkit import MotorKit

# Motor Stuff
motorkit = MotorKit() # Implicit args: address=0x60, i2c=board.I2C()

def _set_throttles(thr1, thr2):
    motorkit.motor1.throttle = thr1
    motorkit.motor2.throttle = thr2

def handle_driving_cmd(cmd):
    if cmd.split()[0] not in ['drive', 'stop', 'rotate', 'arc']:
        return (False, 'Not for me')
    if cmd == 'stop':
        _set_throttles(0, 0)
        return (True, None)
    elif cmd == 'drive':
        _set_throttles(1, 1)
        return (True, None)
    elif cmd == 'rotate left':
        _set_throttles(-1, 1)
        return (True, None)
    elif cmd == 'rotate right':
        _set_throttles(1, -1)
        return (True, None)
    else:
        return (True, 'Malformed driving command')

def driving_stop():
    _set_throttles(0, 0)
