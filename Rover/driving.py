from asyncio import sleep as async_sleep
import math
from adafruit_motorkit import MotorKit
from imu import current_heading
from lidar import get_distances
from nav_utils import HeadingStopper, XStopper, YStopper, heading_diff

# Motor Stuff
motorkit = MotorKit() # Implicit args: address=0x60, i2c=board.I2C()


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
_set_throttles(0, 0)

def driving_stop():
    global action_queue, nav_goal
    _set_throttles(0, 0)
    action_queue.clear()
    nav_goal = None

def _start_first_action():
    global action_queue
    if len(action_queue) > 0:
        (left_thr, right_thr, _) = action_queue[0]
        motorkit.motor1.throttle = left_thr
        motorkit.motor2.throttle = right_thr

def _enqueue_action(left_thr, right_thr, stop_condition):
    global action_queue
    action_queue.append( (left_thr, right_thr, stop_condition) )
    if len(action_queue) == 1:
        # If this is the FIRST action, start it right away
        _start_first_action()
    return (True, None) # Success

def handle_driving_cmd(cmd):
    global nav_goal
    cmd_words = cmd.split()
    if cmd_words[0] not in ['drive', 'stop', 'rotate', 'arc', 'navto']:
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
    if cmd_words[0] == 'navto':
        if len(cmd_words) != 4:
            return (True, 'navto requires 3 arguments')
        try:
            x_mm = int(cmd_words[1])
            y_mm = int(cmd_words[2])
            heading_deg = int(cmd_words[3])
            nav_goal = (x_mm, y_mm, heading_deg)
            _plan_and_start_route()
            return (True, None)
        except ValueError:
            return (True, 'Malformed navto command')
    else:
        return (True, 'Malformed driving command')

def upover_to_xy(up_mm, over_mm):
    x = 1160 - over_mm  # mm
    y = 1060 - up_mm    # mm
    return (x, y)

def _current_xy():
    [dst_up, dist_over] = get_distances()
    x = 1160 - dist_over  # mm
    y = 1060 - dst_up     # mm
    return (x, y)

def _plan_route_to(goal):
    plan = []
    (goal_x, goal_y, final_hdg) = goal
    (curr_x, curr_y) = _current_xy()
    curr_hdg = current_heading()
    print(f"plan ({curr_x}, {curr_y}, {curr_hdg}) to ({goal_x}, {goal_y}, {final_hdg})")
    dx = goal_x - curr_x
    dy = goal_y - curr_y
    print(f"  delta: ({dx}, {dy})")
    if (dx**2 + dy**2) > 400: # More than 20mm away
        hdg_to_goal = math.degrees(math.atan2(dx, dy)) % 360 # (dx,dy) because 0 deg is Up.
        print(f"  bearing to goal: {hdg_to_goal}")
        go_backwards = False
        if hdg_to_goal > 90 and hdg_to_goal < 270:
            hdg_to_goal = (hdg_to_goal + 180) % 360
            go_backwards = True
            print(f"   but go backwards, point to {hdg_to_goal}")
        (dir, n_deg) = heading_diff(curr_hdg, hdg_to_goal)
        if n_deg > 5:
            plan.append( ( -1 if dir == 'left' else 1, 1 if dir == 'left' else -1,
                          HeadingStopper(curr_hdg, dir, hdg_to_goal) ) )
        # Now drive straight to the goal position
        thr = -1 if go_backwards else 1
        if (abs(dx) > abs(dy)):
            # More X movement than Y movement
            plan.append( (thr, thr, XStopper(curr_x, goal_x)) )
        else:
            plan.append( (thr, thr, YStopper(curr_y, goal_y)) )
    else:
        # If we're within 2cm of the goal position, just turn in place to final heading
        (dir, n_deg) = heading_diff(curr_hdg, final_hdg)
        if n_deg > 5:
            plan.append( ( -1 if dir == 'left' else 1, 1 if dir == 'left' else -1,
                        HeadingStopper(curr_hdg, dir, final_hdg) ) )
        else:
            plan = None # No plan needed; we're already there
    print("Planned route:")
    if plan is not None:
        for t in plan:
            print("  ", t[0], t[1], t[2])
    print("------------")
    return plan

def _plan_and_start_route():
    global action_queue, nav_goal
    new_plan = _plan_route_to(nav_goal)
    if new_plan is None or len(new_plan) == 0:
        driving_stop()
        action_queue.clear()
        nav_goal = None
        print("---Navto is complete")
    else:
        action_queue = new_plan
        # Start the first action right away
        _start_first_action()

async def loop_driving():
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
                    _start_first_action()
                else:
                    if nav_goal is None:
                        driving_stop()
                    else:
                        # Give the planner one more chance to put us on track
                        _plan_and_start_route()

async def loop_replan():
    global nav_goal
    while True:
        await async_sleep(1)
        #continue # HACK: Disable replanning for now
        if nav_goal is not None:
            _plan_and_start_route()
