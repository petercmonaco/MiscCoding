
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
        print(f"HeadingStopper: curr={curr_hdg} dir={dir}, target_hdg={self.target_hdg}, breakpoint={self.breakpoint}")

    def _normalize(self, h):
        return h-360 if h > self.breakpoint else h
    
    def should_stop(self, curr_x, curr_y, curr_hdg):
        if (self.dir == 'left'):
            return self._normalize(curr_hdg) <= self.target_hdg
        else:
            return self._normalize(curr_hdg) >= self.target_hdg