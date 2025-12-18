import json
import math

class Point:
    def __init__(self, x, y):
        self.x = round(x)
        self.y = round(y)

    def relative_point(self, angle, distance):
        """
        Calculate a point relative to self at a certain angle and distance.
        """
        rad = math.radians(angle)
        new_x = self.x + distance * math.sin(rad)
        new_y = self.y + distance * math.cos(rad)
        return Point(new_x, new_y)

class Circle:
    def __init__(self, p, r, dir):
        """Dir is either 'L' or 'R' for left or right turn."""
        self.x = p.x
        self.y = p.y
        self.r = r
        self.dir = dir

    def to_dict(self):
        return {
            "type": "circle",
            **self.__dict__
        }

def find_tangent(c1, c2):
    """
    Finds the tangent points between two circles.

    Parameters:
    c1 (Circle): First circle.
    c2 (Circle): Second circle.

    Returns:
    tuple: Tangent points on both circles.
    """
    if (c1.dir == c2.dir):
        dx = c2.x - c1.x
        dy = c2.y - c1.y
        d = math.hypot(dx, dy)

        if d < abs(c1.r - c2.r):
            raise ValueError("Circles are too close or one is contained within the other.")

        angle_between_centers = math.atan2(dy, dx)
        angle_offset = math.acos((c1.r - c2.r) / d)

        if (c1.dir == 'L'):
            abs_angle = angle_between_centers - angle_offset
        else:
            abs_angle = angle_between_centers + angle_offset

        tan_start = Point(c1.x + c1.r * math.cos(abs_angle), c1.y + c1.r * math.sin(abs_angle))
        tan_end = Point(c2.x + c2.r * math.cos(abs_angle), c2.y + c2.r * math.sin(abs_angle))

        return (tan_start, tan_end)
    else:
        return None

def plan_route(arena_width, area_height, x1, y1, hdg1, x2, y2, hdg2, min_radius):
    """
    Plans a route from a starting point (x1, y1) with heading hdg1
    to an ending point (x2, y2) with heading hdg2 and returns the plan
    as a JSON string.

    Parameters:
    arena_width (float): Width of the arena.
    area_height (float): Height of the arena.
    x1 (float): Starting x-coordinate.
    y1 (float): Starting y-coordinate.
    hdg1 (float): Starting heading in degrees.
    x2 (float): Ending x-coordinate.
    y2 (float): Ending y-coordinate.
    hdg2 (float): Ending heading in degrees.
    min_radius (float): Minimum turning radius.

    Returns:
    str: JSON string describing the plan.
    """

    r = min_radius # Later, add option to reduce this if needed for a tight manuever

    start_point = Point(x1, y1)
    end_point = Point(x2, y2)
    start_left_circle = Circle(start_point.relative_point(hdg1 - 90, r), r, "L")
    start_right_circle = Circle(start_point.relative_point(hdg1 + 90, r), r, "R")
    end_left_circle = Circle(end_point.relative_point(hdg2 - 90, r), r, "L")
    end_right_circle = Circle(end_point.relative_point(hdg2 + 90, r), r, "R")

    (p1,p2) = find_tangent(start_left_circle, end_left_circle)
    (p3,p4) = find_tangent(start_right_circle, end_right_circle)

    plan = {
        "width": float(arena_width), 
        "height": float(area_height),
        "shapes": [
            {"type": "rover_start", "x": x1, "y": y1, "hdg": hdg1},
            {"type": "rover_end", "x": x2, "y": y2, "hdg": hdg2},
            start_left_circle.to_dict(),
            start_right_circle.to_dict(),
            end_left_circle.to_dict(),
            end_right_circle.to_dict(),
            {"type": "line", "x1": p1.x, "y1": p1.y, "x2": p2.x, "y2": p2.y},
            {"type": "line", "x1": p3.x, "y1": p3.y, "x2": p4.x, "y2": p4.y}
        ]
    }

    return json.dumps(plan)

# Example
print(plan_route(700, 500, 100, 120, 22, 490, 290, 135, 80))
