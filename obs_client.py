import base64
import hashlib
import json
import websocket


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
                print("TRYING SEND COMMAND WITH PAYLOAD:")
                print(json.dumps(request, indent=4))
                message = self.ws.recv()
                result = json.loads(message)
                print("RESULT:")
                print(json.dumps(result, indent=4))
                return json.loads(message)
            except Exception as e:
                print(f"Retrying command due to error: {e}")

    def close(self):
        self.ws.close()
        print("Connection with OBS closed.")
