
def heading_diff(h1, h2):
    """Returns the # degrees left or right to turn from h1 to h2"""
    d = (h2 - h1 + 180) % 360 - 180
    return ('left' if d < 0 else 'right', abs(d))

# This class helps determine when to stop turning, given
# an initial heading, direction of turn, and target heading.
class HeadingStopper:
    def __init__(self, curr_hdg, dir, target_hdg):
        # In the heading circle (0...360), it's the discontinuity at 0/360 that causes problems.
        # This code creates a new 'breakpoint', and normalizes headings so they have a
        # coninuous sequence of values from one side of the breakpoint to the other.
        # Eg. If we're turning left from 100 to 300, we treat that range as 100...-60.
        # This all works if the "breakpoint" is not on the travel arc.
        self.dir = dir
        midpoint = (curr_hdg + target_hdg)/2
        if (dir == 'left' and curr_hdg > target_hdg) or (dir == 'right' and curr_hdg < target_hdg):
            self.breakpoint = (midpoint + 180) % 360
        else:
            self.breakpoint = midpoint
        self.target_hdg = self._normalize(target_hdg)

    def _normalize(self, h):
        return h-360 if h > self.breakpoint else h
    
    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'left'):
            return self._normalize(curr_hdg) <= self.target_hdg
        else:
            return self._normalize(curr_hdg) >= self.target_hdg
        
    def __str__(self):
        return f"HeadingStopper({self.dir} to hdg {self.target_hdg})"
        
class XStopper:
    def __init__(self, curr_x, target_x):
        self.dir = "right" if target_x > curr_x else "left"
        self.target_x = target_x

    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'right'):
            if curr_x >= self.target_x:
                print(f"XStop! curr_x {curr_x} >= targ {self.target_x}")
            return curr_x >= self.target_x
        else:
            if curr_x <= self.target_x:
                print(f"XStop! curr_x {curr_x} <= targ {self.target_x}")
            return curr_x <= self.target_x
        
    def __str__(self):
        return f"XStopper({self.dir} to x {self.target_x})"

class YStopper:
    def __init__(self, curr_y, target_y):
        self.dir = "Up" if target_y > curr_y else "Down"
        self.target_y = target_y

    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'Up'):
            if curr_y >= self.target_y:
                print(f"YStop! curr_y {curr_y} >= targ {self.target_y}")
            return curr_y >= self.target_y
        else:
            if curr_y <= self.target_y:
                print(f"YStop! curr_y {curr_y} <= targ {self.target_y}")
            return curr_y <= self.target_y
        
    def __str__(self):
        return f"YStopper({self.dir} to y {self.target_y})"
