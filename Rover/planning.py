import json
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def relative_point(self, angle, distance):
        """
        Calculate a point relative to self at a certain angle and distance.

        Parameters:
        angle (float): Heading in degrees.
        distance (float): Distance from the starting point.

        Returns:
        Point: New point at the specified angle and distance.
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

    r = min_radius # Later, add option to reduce this for a tight manuever

    start_point = Point(x1, y1)
    end_point = Point(x2, y2)
    start_left_circle = Circle(start_point.relative_point(hdg1 - 90, r), r, "L")
    start_right_circle = Circle(start_point.relative_point(hdg1 + 90, r), r, "R")
    end_left_circle = Circle(end_point.relative_point(hdg2 - 90, r), r, "L")
    end_right_circle = Circle(end_point.relative_point(hdg2 + 90, r), r, "R")

    plan = {
        "width": float(arena_width), 
        "height": float(area_height),
        "shapes": [
            {"type": "rover_start", "x": x1, "y": y1, "hdg": hdg1},
            {"type": "rover_end", "x": x2, "y": y2, "hdg": hdg2},
            start_left_circle.to_dict(),
            start_right_circle.to_dict(),
            end_left_circle.to_dict(),
            end_right_circle.to_dict()
        ]
    }

    return json.dumps(plan)

# Example
print(plan_route(700, 500, 100, 120, 22, 490, 290, 90, 80))
