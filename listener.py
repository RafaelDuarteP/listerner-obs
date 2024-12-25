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
DEFAULT_AUDIO_SOURCE = "defaultAudioSource"

# UDP Listener Configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 12345


class OBSWebSocketClient:
    def __init__(self, host, port, password):
        self.ws = websocket.WebSocket()
        self.url = f"ws://{host}:{port}"
        self.password = password

    def connect(self):
        self.ws.connect(self.url)

    def authenticate(self):
        message = self.ws.recv()
        result = json.loads(message)
        auth = self._build_auth_string(
            result["d"]["authentication"]["salt"],
            result["d"]["authentication"]["challenge"],
        )

        payload = {
            "op": 1,
            "d": {"rpcVersion": 1, "authentication": auth, "eventSubscriptions": 1000},
        }
        self.ws.send(json.dumps(payload))
        message = self.ws.recv()
        result = json.loads(message)
        print(json.dumps(result, indent=4))
        print("Authenticated with OBS")

    def _build_auth_string(self, salt, challenge):
        secret = base64.b64encode(
            hashlib.sha256((self.password + salt).encode("utf-8")).digest()
        )
        auth = base64.b64encode(
            hashlib.sha256(secret + challenge.encode("utf-8")).digest()
        ).decode("utf-8")
        return auth

    def send_command(self, request):
        while True:
            try:
                self.ws.send(json.dumps(request))
                message = self.ws.recv()
                return json.loads(message)
            except Exception as e:
                print(f"Retrying command due to error: {e}")

    def close(self):
        self.ws.close()


class UDPListener:
    def __init__(self, ip, port, handler):
        self.ip = ip
        self.port = port
        self.handler = handler

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))
        print(f"UDP listener started on {self.ip}:{self.port}")

        while True:
            data, addr = sock.recvfrom(1024)
            self.handler(data)


class OBSController:
    def __init__(self, obs_client, default_scene, default_audio_source):
        self.obs_client = obs_client
        self.default_scene = default_scene
        self.default_audio_source = default_audio_source

    def get_payload(self, request_type, request_data):
        return {
            "op": 6,
            "d": {
                "requestId": uuid.uuid4().hex,
                "requestType": request_type,
                "requestData": request_data,
            },
        }

    def toggle_item_scene(self, scene_item_id):
        finished = False
        while not finished:
            try:
                result = self.obs_client.send_command(
                    self.get_payload(
                        "GetSceneItemEnabled",
                        {
                            "sceneItemId": scene_item_id,
                            "sceneName": self.default_scene,
                        },
                    )
                )
                if result["op"] == 7:
                    enabled = result["d"]["responseData"]["sceneItemEnabled"]
                    result = self.obs_client.send_command(
                        self.get_payload(
                            "SetSceneItemEnabled",
                            {
                                "sceneItemId": scene_item_id,
                                "sceneName": self.default_scene,
                                "sceneItemEnabled": not enabled,
                            },
                        )
                    )
                    if result["op"] == 7:
                        finished = True
            except Exception as e:
                print(f"An error occurred: {e}")

    def transition(self, transition_name, duration):
        try:
            self.obs_client.send_command(
                self.get_payload(
                    "SetCurrentSceneTransition", {"transitionName": transition_name}
                )
            )
            self.obs_client.send_command(
                self.get_payload(
                    "SetCurrentSceneTransitionDuration",
                    {"transitionDuration": duration},
                )
            )
            self.obs_client.send_command(
                self.get_payload("TriggerStudioModeTransition", {})
            )
        except Exception as e:
            print(f"An error occurred during transition: {e}")

    def toggle_mute(self):
        self.obs_client.send_command(
            self.get_payload(
                "ToggleInputMute",
                {"inputName": self.default_audio_source},
            )
        )

    def start_record(self):
        self.obs_client.send_command(self.get_payload("StartRecord", {}))

    def start_live(self):
        self.obs_client.send_command(self.get_payload("StartStream", {}))

    def stop(self):
        self.obs_client.send_command(self.get_payload("StopStream", {}))
        self.obs_client.send_command(self.get_payload("StopRecord", {}))


class MessageHandler:
    def __init__(self, controller):
        self.controller = controller

    def handle(self, message):
        message = message.decode("utf-8").strip()

        match_toggle_item = re.match(r"toggleItem(\d+)", message)
        match_transition = re.match(r"transition([a-zA-Z]+)(\d+)", message)

        if match_toggle_item:
            scene_item_id = int(match_toggle_item.group(1))
            self.controller.toggle_item_scene(scene_item_id)
            print(f"Toggled item {scene_item_id}")

        elif match_transition:
            self.controller.transition(
                match_transition.group(1), int(match_transition.group(2))
            )
            print(
                f"Transition {match_transition.group(1)} with {match_transition.group(2)}"
            )

        elif message == "toggleMute":
            self.controller.toggle_mute()
            print(f"Toggled mute for {self.controller.default_audio_source}.")

        elif message == "startRecord":
            self.controller.start_record()
            print("Started recording.")

        elif message == "startLive":
            self.controller.start_live()
            print("Started live streaming.")

        elif message == "stop":
            self.controller.stop()
            print("Stopped live streaming and recording.")


def main():
    obs_client = OBSWebSocketClient(OBS_HOST, OBS_PORT, OBS_PASS)
    obs_client.connect()
    obs_client.authenticate()

    controller = OBSController(obs_client, DEFAULT_SCENE, DEFAULT_AUDIO_SOURCE)
    message_handler = MessageHandler(controller)

    udp_listener = UDPListener(UDP_IP, UDP_PORT, message_handler.handle)
    udp_listener.start()


if __name__ == "__main__":
    main()
