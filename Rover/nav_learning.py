
import time

class RegressionLearner:
    def __init__(self, x1, y1, x2, y2, max_points):
        self.points = [(x1, y1), (x2, y2)]
        self.sum_x = x1 + x2
        self.sum_y = y1 + y2
        self.sum_xx = x1*x1 + x2*x2
        self.sum_xy = x1*y1 + x2*y2
        self.max_points = max_points

    def add_point(self, x, y):
        self.points.append((x, y))
        self.sum_x += x
        self.sum_y += y
        self.sum_xx += x*x
        self.sum_xy += x*y
        while len(self.points) > self.max_points:
            (old_x, old_y) = self.points.pop(0)
            self.sum_x -= old_x
            self.sum_y -= old_y
            self.sum_xx -= old_x*old_x
            self.sum_xy -= old_x*old_y

    def _get_regression(self):
        n = len(self.points)
        denom = n*self.sum_xx - self.sum_x*self.sum_x
        if denom == 0:
            return (0, 0)
        m = (n*self.sum_xy - self.sum_x*self.sum_y) / denom
        b = (self.sum_y - m*self.sum_x) / n
        return (m, b)
    
    def predict(self, x):
        (m, b) = self._get_regression()
        return m*x + b

# Create a separate regression learner for each 20 degree sector of headings.
# Expected turning behavior, as a function of throttle skew is:
#   (t1-t2)/(t1+t2) = 48/R
# R is the turning radius
# 48 is 1/2 the distance between wheels, in mm.
# We'll be setting y = (t1-t2)/(t1+t2) and x = 48/R, so ideally the line we learn is y=x.
# Max expected skew is (1-0.7)/(1+0.7) = 0.176.
# So we'll prime each learner with two points (-0.1, -0.1) and (0.1, 0.1).
#
NUM_SECTORS = 18
learners = [RegressionLearner(-0.1, -0.1, 0.1, 0.1, 25) for _ in range(NUM_SECTORS)]

def hdg_to_sector(hdg):
    return int(round(hdg/(360/NUM_SECTORS), 0)) % NUM_SECTORS

log = print
def set_wlogger(l):
    global log
    log = l

def _learn(th1, th2, hdg, r):
    if (th1 + th2) == 0 or r == 0:
        return
    i = hdg_to_sector(hdg)
    skew = (th1 - th2) / (th1 + th2)
    x = 48/r
    pre_estimate = learners[i].predict(0)
    learners[i].add_point(x, skew)
    post_estimate = learners[i].predict(0)
    log(f"Learned: hdg {hdg} = sector {i}: pt ({x}, {skew}),  pred {round(pre_estimate, 4)} -> {round(post_estimate, 4)}")

def suggest_throttles(hdg, inv_radius):
    i = hdg_to_sector(hdg)
    skew = learners[i].predict(48*inv_radius)
    if skew > 0:
        t1 = 1.0
        t2 = (1-skew)/(1+skew)
    else:
        t2 = 1.0
        t1 = (1+skew)/(1-skew)
    return (t1, t2)

def dump_learners():
    for i in [16, 17, 0, 1, 2]:
        log(f"Sector {i}: {suggest_throttles(i*360/NUM_SECTORS, 0)}")

# Look at successive throttle settings and actual headings. Break the stream of calls
# into segments when throttles are unchanged for more than a second. Learn from the
# change in heading over that time, and correlate it with the throttle settings.
initial_hdg = None
initial_time = None
initial_thr1 = None
initial_thr2 = None
initial_x = None
initial_y = None
def learn(thr1, thr2, x, y, hdg):
    global initial_hdg, initial_time, initial_thr1, initial_thr2, initial_x, initial_y
    if (thr1 == 0 and thr2 == 0):
        initial_time = None
        return
    if initial_hdg is None or initial_time is None or initial_thr1 != thr1 or initial_thr2 != thr2:
        initial_hdg = hdg
        initial_time = time.monotonic()
        initial_x = x
        initial_y = y
        initial_thr1 = thr1
        initial_thr2 = thr2
        return
    if time.monotonic() - initial_time > 1.0:
        # learn from the change in heading over the last second, and correlate it with the throttle settings
        delta_hdg = (hdg - initial_hdg) % 360
        if delta_hdg > 180:
            delta_hdg -= 360
        dist_traveled = ((x - initial_x)**2 + (y - initial_y)**2)**0.5
        effective_radius = dist_traveled / (delta_hdg * 3.14159 / 180) if delta_hdg != 0 else float('inf')
        i_hdg_cat = hdg_to_sector(initial_hdg)
        log(f"Thr=({thr1},{thr2}), i_sect={i_hdg_cat}, d_hdg={delta_hdg}, dist={dist_traveled}, Effective_R={effective_radius}")
        _learn(initial_thr1, initial_thr2, initial_hdg, effective_radius)
        initial_hdg = hdg
        initial_time = time.monotonic()
        initial_x = x
        initial_y = y
    