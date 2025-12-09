# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
from asyncio import create_task, gather, run
from asyncio import sleep as async_sleep

import socketpool

from adafruit_httpserver import GET, Request, Response, Server, Websocket

#print("ESP32-S2 WebClient Test")
#print(f"My MAC address: {[hex(i) for i in wifi.radio.mac_address]}")

#print("Available WiFi networks:")
#for network in wifi.radio.start_scanning_networks():
#    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
#                                             network.rssi, network.channel))
#wifi.radio.stop_scanning_networks()

print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
print(f"My IP address: {wifi.radio.ipv4_address}")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
server = Server(pool, debug=True)

websocket: Websocket = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Whiteboard Rover</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 20px auto; }
        #log { border: 1px solid #ccc; padding: 10px; height: 200px; overflow-y: scroll; margin-bottom: 10px; }
        #messageInput { width: calc(100% - 70px); padding: 8px; }
        #sendButton { width: 60px; padding: 8px; }
        .sent { color: blue; }
        .received { color: green; }
        .status { color: gray; font-size: 0.8em; }
    </style>
</head>
<body>
    <h1>Whiteboard Rover Comm Interface</h1>

    <div>
        <label for="wsUrl">WebSocket URL:</label>
        <input type="text" id="wsUrl" value="ws://IPADDR:5000/connect-websocket" size="40">
        <button id="connectButton">Connect</button>
        <button id="disconnectButton" disabled>Disconnect</button>
    </div>
    <p class="status">Status: <span id="connectionStatus">Closed</span></p>

    <div id="log"></div>

    <form id="messageForm">
        <input type="text" id="messageInput" placeholder="Type a message...">
        <button type="submit" id="sendButton" disabled>Send</button>
    </form>

    <script>
        const log = document.getElementById('log');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const connectButton = document.getElementById('connectButton');
        const disconnectButton = document.getElementById('disconnectButton');
        const statusSpan = document.getElementById('connectionStatus');
        const wsUrlInput = document.getElementById('wsUrl');
        let socket;

        function appendLog(message, className) {
            const item = document.createElement('div');
            item.classList.add(className);
            item.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            log.appendChild(item);
            // Scroll to the bottom
            log.scrollTop = log.scrollHeight - log.clientHeight;
        }

        connectButton.addEventListener('click', () => {
            const url = wsUrlInput.value;
            if (!url) return;

            socket = new WebSocket(url);

            socket.onopen = (event) => {
                statusSpan.textContent = 'Connected';
                connectButton.disabled = true;
                disconnectButton.disabled = false;
                sendButton.disabled = false;
                appendLog('Connection established', 'status');
            };

            socket.onmessage = (event) => {
                appendLog('Received: ' + event.data, 'received');
            };

            socket.onclose = (event) => {
                statusSpan.textContent = 'Closed';
                connectButton.disabled = false;
                disconnectButton.disabled = true;
                sendButton.disabled = true;
                appendLog('Connection closed', 'status');
            };

            socket.onerror = (error) => {
                appendLog('Error: ' + error.message, 'status');
            };
        });

        disconnectButton.addEventListener('click', () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        });

        document.getElementById('messageForm').addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent page reload
            const message = messageInput.value;
            if (socket && socket.readyState === WebSocket.OPEN && message) {
                socket.send(message);
                appendLog('Sent: ' + message, 'sent');
                messageInput.value = ''; // Clear input box
            }
        });
    </script>
</body>
</html>
"""


@server.route("/", GET)
def client(request: Request):
    return Response(request, HTML_TEMPLATE.replace("IPADDR", str(wifi.radio.ipv4_address)), content_type="text/html")


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
