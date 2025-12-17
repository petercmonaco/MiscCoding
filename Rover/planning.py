import json
import math

def relative_point(x, y, angle, distance):
    """
    Calculate a point relative to (x, y) at a certain angle and distance.

    Parameters:
    x (float): Starting x-coordinate.
    y (float): Starting y-coordinate.
    angle (float): Heading in degrees.
    distance (float): Distance from the starting point.

    Returns:
    tuple: New (x, y) coordinates.
    """
    rad = math.radians(angle)
    new_x = x + distance * math.sin(rad)
    new_y = y + distance * math.cos(rad)
    return new_x, new_y

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

    start_left_center_x, start_left_center_y = relative_point(x1, y1, hdg1 - 90, min_radius)
    start_right_center_x, start_right_center_y = relative_point(x1, y1, hdg1 + 90, min_radius)

    plan = {
        "width": float(arena_width), 
        "height": float(area_height),
        "shapes": [
            {
            "type": "rover_end",
            "x": x2,
            "y": y2,
            "hdg": hdg2
            },
            {
            "type": "rover_start",
            "x": x1,
            "y": y1,
            "hdg": hdg1},
        {"type": "circle",
         "x": start_left_center_x,
         "y": start_left_center_y,
         "r": min_radius},

        {"type": "circle",
         "x": start_right_center_x,
         "y": start_right_center_y,
         "r": min_radius}
        ]
    }

    return json.dumps(plan)

# Example
print(plan_route(700, 500, 100, 120, 22, 490, 290, 90, 80))
