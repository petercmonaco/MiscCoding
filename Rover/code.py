# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ssl
from driving import driving_stop, handle_driving_cmd, handle_driving
from imu import current_heading
from lidar import get_distances
import wifi
import socketpool
import adafruit_requests
from asyncio import create_task, gather, run
from asyncio import sleep as async_sleep
from adafruit_httpserver import GET, Request, Response, Server, Websocket
from display import display_cmd, display_battery, display_distances, display_heading
import board
import alarm
import adafruit_max1704x

print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
print(f"My IP address: {wifi.radio.ipv4_address}")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
server = Server(pool, debug=True)

websocket: Websocket = None

@server.route("/", GET)
def client(request: Request):
    file_path = "client_ui.html"
    try:
        with open(file_path, "r") as file:
            file_content = file.read()
        print(f"{file_path} content loaded successfully:")
        return Response(request, file_content.replace("IPADDR", str(wifi.radio.ipv4_address)), content_type="text/html")
    except OSError as e:
        print(f"Error opening or reading file {file_path}: {e}")
        return Response(request, f"Error opening or reading file {file_path}: {e}", content_type="text")


@server.route("/connect-websocket", GET)
def connect_client(request: Request):
    global websocket

    if websocket is not None:
        websocket.close()  # Close any existing connection

    websocket = Websocket(request)

    return websocket


server.start(str(wifi.radio.ipv4_address))

# Battery monitor
bm = adafruit_max1704x.MAX17048(board.I2C())

def execute_cmd(cmd):
    if cmd == 'sleep':
        driving_stop()
        alarm.exit_and_deep_sleep_until_alarms(alarm.pin.PinAlarm(pin=board.D0, value=False))
    elif cmd == 'ping':
        websocket.send_message("Pong", fail_silently=True)
    elif cmd == 'status':
        websocket.send_message(f"Battery: {bm.cell_percent:.1f}%\nHeading: {current_heading():.1f}", fail_silently=True)
    else:
        (is_for_me, msg) = handle_driving_cmd(cmd)
        if is_for_me:
            if msg:
                websocket.send_message(msg, fail_silently=True)
            return
    
    websocket.send_message("Unknown command: " + cmd, fail_silently=True)

async def handle_http_requests():
    while True:
        server.poll()

        await async_sleep(0)


async def handle_websocket_requests():
    while True:
        if websocket is not None:
            if (data := websocket.receive(fail_silently=True)) is not None:
                print("Received: "+data)
                # websocket.send_message("Thanks for: " + data, fail_silently=True)
                display_cmd(data)
                execute_cmd(data)

        await async_sleep(0)

async def update_battery():
    await async_sleep(3) # Wait for battery data to init
    while True:
        display_battery(f"{bm.cell_percent:.1f}%")
        await async_sleep(15)

async def update_heading():
    while True:
        await async_sleep(1)
        display_heading(f"{current_heading():.1f}°")

async def update_distance():
    while True:
        await async_sleep(1)
        display_distances(*get_distances())


async def main():
    await gather(
        create_task(handle_http_requests()),
        create_task(handle_websocket_requests()),
        create_task(update_battery()),
        create_task(update_heading()),
        create_task(update_distance()),
        create_task(handle_driving()),
        ##create_task(do_ranging()),
    )


run(main())
