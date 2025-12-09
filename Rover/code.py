# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ssl
import wifi
import socketpool
import adafruit_requests
from asyncio import create_task, gather, run
from asyncio import sleep as async_sleep
from adafruit_httpserver import GET, Request, Response, Server, Websocket

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


async def handle_http_requests():
    while True:
        server.poll()

        await async_sleep(0)


async def handle_websocket_requests():
    while True:
        if websocket is not None:
            if (data := websocket.receive(fail_silently=True)) is not None:
                print("Received: "+data)
                websocket.send_message("Thanks for: " + data, fail_silently=True)

        await async_sleep(0)


async def main():
    await gather(
        create_task(handle_http_requests()),
        create_task(handle_websocket_requests()),
    )


run(main())
