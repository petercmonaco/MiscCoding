from asyncio import sleep as async_sleep
from adafruit_motorkit import MotorKit
from imu import current_heading
from lidar import get_distances
from utils import HeadingStopper

# Motor Stuff
motorkit = MotorKit() # Implicit args: address=0x60, i2c=board.I2C()

class XStopper:
    def __init__(self, curr_x, target_x):
        self.dir = "Left" if target_x > curr_x else "Right"
        self.target_x = target_x

    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'Left'):
            return curr_x >= self.target_x
        else:
            return curr_x <= self.target_x

class YStopper:
    def __init__(self, curr_y, target_y):
        self.dir = "Up" if target_y > curr_y else "Down"
        self.target_y = target_y

    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'Up'):
            return curr_y >= self.target_y
        else:
            return curr_y <= self.target_y

def _set_throttles(thr1, thr2):
    motorkit.motor1.throttle = thr1
    motorkit.motor2.throttle = thr2
    return (True, None) # Success; returning this tuple is helpful for next layer up

WHEEL_SEP = 98 # mm

# Driving state
# Can be simply a list of (left_throttle, right_throttle, stop_condition) tuples,
# or that plus a nav_goal.
# If there is a nav_goal, periodically clear the action_queue and recompute it.
action_queue = [] # List of (left_throttle, right_throttle, stop_condition) tuples
nav_goal = None # If not None, a (x_mm, y_mm, heading_deg) tuple

def driving_stop():
    global action_queue, nav_goal
    _set_throttles(0, 0)
    action_queue.clear()
    nav_goal = None

def _enqueue_action(left_thr, right_thr, stop_condition):
    global action_queue
    action_queue.append( (left_thr, right_thr, stop_condition) )
    if len(action_queue) == 1:
        # If this is the only action, start it right away
        motorkit.motor1.throttle = left_thr
        motorkit.motor2.throttle = right_thr
    return (True, None) # Success

def handle_driving_cmd(cmd):
    cmd_words = cmd.split()
    if cmd_words[0] not in ['drive', 'stop', 'rotate', 'arc']:
        return (False, 'Not for me')
    if cmd == 'stop':
        driving_stop()
        return (True, None)
    if cmd == 'drive':
        return _enqueue_action(1, 1, None)
    if cmd == 'rotate left':
        return _enqueue_action(-1, 1, None)
    if cmd == 'rotate right':
        return _enqueue_action(1, -1, None)
    if cmd_words[0] == 'arc':
        try:
            arc_dir = cmd_words[1]
            arc_radius = int(cmd_words[2])
            arc_stop_at_hdg = int(cmd_words[3])
            inner_wheel_speed = (arc_radius - (WHEEL_SEP / 2)) / (arc_radius + (WHEEL_SEP / 2))
            stop_condition = HeadingStopper(current_heading(), arc_dir, arc_stop_at_hdg)
            if arc_dir == 'left':
                _enqueue_action(inner_wheel_speed, 1, stop_condition)
            elif arc_dir == 'right':
                _enqueue_action(1, inner_wheel_speed, stop_condition)
            else:
                return (True, 'Invalid arc direction')
            return (True, None)
        except ValueError:
            return (True, 'Malformed arc cmd')
    else:
        return (True, 'Malformed driving command')

def _current_xy():
    [dst_up, dist_over] = get_distances()
    x = 1040 - dist_over  # mm
    y = 1060 - dst_up     # mm
    return (x, y)

async def handle_driving():
    global action_queue
    while True:
        await async_sleep(0.01)
        if len(action_queue) > 0 and action_queue[0][2] is not None:
            stop_condition = action_queue[0][2]
            (curr_x, curr_y) = _current_xy()
            if stop_condition.should_stop(curr_x, curr_y, current_heading()):
                action_queue.pop(0)
                if len(action_queue) > 0:
                    # Start the next action
                    (left_thr, right_thr, _) = action_queue[0]
                    motorkit.motor1.throttle = left_thr
                    motorkit.motor2.throttle = right_thr
                else:
                    driving_stop()
