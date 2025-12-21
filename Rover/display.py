# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""
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

text_cmd = "Waiting..."
text_battery = "??.??%"
text_heading = "??"
text_distance = "??"

# Draw a label
ta1 = label.Label(terminalio.FONT, text=f"Cmd: {text_cmd}", color=TEXT_COLOR)
ta1.y = 10
ta2 = label.Label(terminalio.FONT, text=f"Bat: {text_battery}", color=TEXT_COLOR)
ta2.y = 20
ta3 = label.Label(terminalio.FONT, text=f"Hdg: {text_heading}", color=TEXT_COLOR)
ta3.y = 30
ta4 = label.Label(terminalio.FONT, text=f"Dst: {text_distance}mm", color=TEXT_COLOR)
ta4.y = 40
ta5 = label.Label(terminalio.FONT, text="Ln5:", color=TEXT_COLOR)
ta5.y = 50
text_group = displayio.Group(
    scale=FONTSCALE,
    x=int(BORDER*1.5),
    y=10,
)
text_group.append(ta1)
text_group.append(ta2)
text_group.append(ta3)
text_group.append(ta4)
text_group.append(ta5)

splash.append(text_group)

def display_cmd(cmd):
    global ta1, text_cmd
    if cmd != text_cmd:
        text_cmd = cmd
        ta1.text = f"Cmd: {text_cmd}"

def display_battery(b):
    global ta2, text_battery
    if b != text_battery:
        text_battery = b
        ta2.text = f"Bat: {text_battery}"

def display_heading(h):
    global ta3, text_heading
    if h != text_heading:
        text_heading = h
        ta3.text = f"Hdg: {text_heading}"

def display_distance(d):
    global ta4, text_distance
    if d != text_distance:
        text_distance = d
        ta4.text = f"Dst: {text_distance}"