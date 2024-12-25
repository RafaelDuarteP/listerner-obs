import base64
import hashlib
import json
import uuid
import websocket
import asyncio
import json
import socket
import re

# Variaveis que serão preenchidas pelo usuario

OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASS = "Iw5ja6Pxv6TkJICO"

DEFAULT_SCENE = "tela"

DEFAULT_AUDIO_SOURCE = "Desktop Audio"

TRANSITION_NAME = "Fade"

# UDP Listener Configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 12345

ws = websocket.WebSocket()
url = "ws://{}:{}".format(OBS_HOST, OBS_PORT)
ws.connect(url)


def getPayload(requestType, requestData):
    return {
        "op": 6,
        "d": {
            "requestId": uuid.uuid4().hex,
            "requestType": requestType,
            "requestData": requestData,
        },
    }


EVENT_REQUESTS_TYPES = {
    "SET_TRANSITION": "SetCurrentSceneTransition",
    "SET_TRANSITION_DURATION": "SetCurrentSceneTransitionDuration",
    "TRANSITION": "TriggerStudioModeTransition",
    "GET_ITEM_SCENE": "GetSceneItemEnabled",
    "TOGGLE_ITEM_SCENE": "SetSceneItemEnabled",
    "TOGGLE_MUTE": "ToggleInputMute",
    "START_RECORD": "StartRecord",
    "START_LIVE": "StartStream",
    "STOP_LIVE": "StopStream",
    "STOP_RECORD": "StopRecord",
}


def _build_auth_string(salt, challenge):
    secret = base64.b64encode(
        hashlib.sha256((OBS_PASS + salt).encode("utf-8")).digest()
    )
    auth = base64.b64encode(
        hashlib.sha256(secret + challenge.encode("utf-8")).digest()
    ).decode("utf-8")
    return auth


def auth():
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
    result = json.loads(message)
    print(json.dumps(result, indent=4))
    print("Authenticated with OBS")


def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"UDP listener started on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        handle_udp_message(data)


def toggle_item_scene(sceneItemId):
    try:
        result = send_obs_command(
            getPayload(
                EVENT_REQUESTS_TYPES["GET_ITEM_SCENE"],
                {
                    "sceneItemId": sceneItemId,
                    "sceneName": DEFAULT_SCENE,
                },
            )
        )
        enabled = result["d"]["responseData"]["sceneItemEnabled"]
        send_obs_command(
            getPayload(
                EVENT_REQUESTS_TYPES["TOGGLE_ITEM_SCENE"],
                {
                    "sceneItemId": sceneItemId,
                    "sceneName": DEFAULT_SCENE,
                    "sceneItemEnabled": not enabled,
                },
            )
        )

    except Exception as e:
        print(f"An error occurred: {e}")


def transition(transitionName, duration):
    try:
        send_obs_command(
            getPayload(
                EVENT_REQUESTS_TYPES["SET_TRANSITION"],
                {
                    "transitionName": transitionName,
                },
            )
        )
        send_obs_command(
            getPayload(
                EVENT_REQUESTS_TYPES["SET_TRANSITION_DURATION"],
                {
                    "transitionDuration": duration,
                },
            )
        )
        send_obs_command(getPayload(EVENT_REQUESTS_TYPES["TRANSITION"], {}))
    except Exception as e:
        print(f"An error occurred during transition: {e}")


def toggle_mute():
    send_obs_command(
        getPayload(
            EVENT_REQUESTS_TYPES["TOGGLE_MUTE"],
            {
                "inputName": DEFAULT_AUDIO_SOURCE,
            },
        )
    )

def start_record():
    send_obs_command(
        getPayload(
            EVENT_REQUESTS_TYPES["START_RECORD"],
            {},
        )
    )

def start_live():
    send_obs_command(
        getPayload(
            EVENT_REQUESTS_TYPES["START_LIVE"],
            {},
        )
    )

def stop():
    send_obs_command(
        getPayload(
            EVENT_REQUESTS_TYPES["STOP_LIVE"],
            {},
        )
    )
    send_obs_command(
        getPayload(
            EVENT_REQUESTS_TYPES["STOP_RECORD"],
            {},
        )
    )

def handle_udp_message(message):
    """Handle incoming UDP messages."""
    message = message.decode("utf-8").strip()

    match_toggle_item = re.match(r"toggleItem(\d+)", message)
    match_transition = re.match(r"transition([a-zA-Z]+)(\d+)", message)
    if match_toggle_item:
        scene_item_id = int(match_toggle_item.group(1))
        toggle_item_scene(scene_item_id)
        print(f"Toggle item {scene_item_id}")

    elif match_transition:
        transition(match_transition.group(1), int(match_transition.group(2)))
        print(
            f"Transition {match_transition.group(1)} with {match_transition.group(2)}"
        )

    elif message == "toggleMute":
        toggle_mute()
        print(f"Toggled mute for {DEFAULT_AUDIO_SOURCE}.")

    elif message == "startRecord":
        start_record()
        print("Started recording.")

    elif message == "startLive":
        start_live()
        print("Started live streaming.")

    elif message == "stop":
        stop()
        print("Stopped live streaming and recording.")


def send_obs_command(request):
    ws.send(json.dumps(request))
    message = ws.recv()
    result = json.loads(message)
    return result


def connect_to_obs():
    auth()
    udp_listener()


if __name__ == "__main__":
    connect_to_obs()
