import board
import terminalio
import displayio
from adafruit_display_text import label

# First set some parameters used for shapes and text
BORDER = 10
FONTSCALE = 2
BACKGROUND_COLOR = 0x80bfff  # Light Blue
FOREGROUND_COLOR = 0x000000  # Black
TEXT_COLOR = 0xffffff # White

display = board.DISPLAY

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(
    display.width - BORDER * 2, display.height - BORDER * 2, 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = FOREGROUND_COLOR
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

last_text = [
    "Cmd: Waiting...",
    "Bat: ??.??%",
    "Hdg: ??",
    "Dst: ??",
    "X/Y: ??"
]

text_areas = [None] * len(last_text)
label_y = 10
for i, t in enumerate(last_text):
    text_areas[i] = label.Label(terminalio.FONT, text=last_text[i], color=TEXT_COLOR)
    text_areas[i].y = label_y
    label_y += 10

text_group = displayio.Group(
    scale=FONTSCALE,
    x=int(BORDER*1.5),
    y=10,
)
for ta in text_areas:
    text_group.append(ta)

splash.append(text_group)

def _update_line_text(i, new_text):
    global text_areas, last_text
    if last_text[i] != new_text:
        last_text[i] = new_text
        text_areas[i].text = new_text

def display_cmd(cmd):
    _update_line_text(0, f"Cmd: {cmd}")

def display_battery(b):
    _update_line_text(1, f"Bat: {b}%")

def display_heading(h):
    _update_line_text(2, f"Hdg: {h}")

def display_distances(d):
    if d is not None and len(d) == 2:
        _update_line_text(3, f"Dst: {d[0]}mm, {d[1]}mm")
    else:
        _update_line_text(3, "Dst: None")

def display_xy(d):
    if d is not None and len(d) == 2:
        _update_line_text(4, f"X/Y: {d[0]}, {d[1]}")
    else:
        _update_line_text(4, "X/Y: None")
