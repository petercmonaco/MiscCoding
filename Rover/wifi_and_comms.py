import adafruit_datetime as datetime
import os
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_httpserver import GET, Request, Response, Server, Websocket
from asyncio import sleep as async_sleep

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

command_handler = None
def set_command_handler(h):
    global command_handler
    command_handler = h

async def handle_http_requests():
    while True:
        server.poll()

        await async_sleep(0)

async def handle_websocket_requests():
    global websocket, command_handler
    while True:
        if websocket is not None:
            if (data := websocket.receive(fail_silently=True)) is not None:
                print("Received: "+data)
                if command_handler is not None:
                    command_handler(data)

        await async_sleep(0)

def send_message(msg):
    global websocket
    if websocket is not None:
        websocket.send_message(msg, fail_silently=True)

def wlog(msg: str):
    if websocket is not None:
        # Get the current date and time as a datetime object
        now = datetime.datetime.now()
        # Just show minutes, seconds, milliseconds
        full_msg = f"WLOG{now.minute:02}:{now.second:02}.{now.microsecond // 1000:03} - {msg}"
        websocket.send_message(full_msg, fail_silently=True)
