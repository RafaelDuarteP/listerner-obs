import logging
import base64
import hashlib
import json

logging.basicConfig(level=logging.DEBUG)
import websocket
import asyncio
import json
import socket

LOG = logging.getLogger(__name__)

OBS_HOST = "localhost"
OBS_PORT = 4455  # or whatever port you use
OBS_PASS = "Iw5ja6Pxv6TkJICO"

# UDP Listener Configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 12345

id = 1

ws = websocket.WebSocket()
url = "ws://{}:{}".format(OBS_HOST, OBS_PORT)
ws.connect(url)


def _build_auth_string(salt, challenge):
    secret = base64.b64encode(
        hashlib.sha256((OBS_PASS + salt).encode("utf-8")).digest()
    )
    auth = base64.b64encode(
        hashlib.sha256(secret + challenge.encode("utf-8")).digest()
    ).decode("utf-8")
    return auth


async def auth():
    message = ws.recv()
    result = json.loads(message)
    auth = _build_auth_string(
        result["d"]["authentication"]["salt"],
        result["d"]["authentication"]["challenge"],
    )

    payload = {
        "op": 1,
        "d": {"rpcVersion": 1, "authentication": auth, "eventSubscriptions": 1000},
    }
    ws.send(json.dumps(payload))
    message = ws.recv()
    # Message Identified...or so we assume...probably good to check if this is empty or not.
    result = json.loads(message)
    print(result)


async def udp_listener(websocket):
    """Start a UDP listener for incoming commands."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP listener started on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received message: {data.decode('utf-8')} from {addr}")
        await handle_udp_message(data, websocket)


async def handle_udp_message(message, websocket):
    """Handle incoming UDP messages."""
    message = message.decode("utf-8").strip()

    if message == "toggleMute":
        send_obs_command(websocket, "ToggleMute", {"inputName": "defaultAudioSource"})
        print("Toggled mute for 'Desktop Audio'.")

    elif message == "startRecord":
        # await send_obs_command(websocket, "StartRecord")
        print("Started recording.")

    elif message == "startLive":
        # await send_obs_command(websocket, "StartStream")
        print("Started live streaming.")

    elif message == "stop":
        # await send_obs_command(websocket, "StopRecord")
        # await send_obs_command(websocket, "StopStream")
        print("Stopped recording and live streaming.")


def send_obs_command(websocket, command, params=None):
    """Send a command to the OBS WebSocket server."""
    request = {
        "op": 6,
        "d": {
            "requestId": "SetMeSomeFrigginScenesYo",
            "requestType": "ToggleInputMute",
            "requestData": {"inputName": "defaultAudioSource"},
        },
    }

    ws.send(json.dumps(request))
    message = ws.recv()
    # Message Identified...or so we assume...probably good to check if this is empty or not.
    result = json.loads(message)
    print(result)


async def connect_to_obs():
    await auth()
    await udp_listener(ws)
    


if __name__ == "__main__":
    asyncio.run(connect_to_obs())
