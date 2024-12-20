import logging
import base64
import hashlib
import json
logging.basicConfig(level=logging.DEBUG)
import websocket

LOG = logging.getLogger(__name__)

host = "localhost"
port = 4455 #or whatever port you use
password = "Iw5ja6Pxv6TkJICO"

id = 1

ws = websocket.WebSocket()
url = "ws://{}:{}".format(host, port)
ws.connect(url)

def _build_auth_string(salt, challenge):
    secret = base64.b64encode(
        hashlib.sha256(
            (password + salt).encode('utf-8')
        ).digest()
    )
    auth = base64.b64encode(
        hashlib.sha256(
            secret + challenge.encode('utf-8')
        ).digest()
    ).decode('utf-8')
    return auth



def _auth():
    message = ws.recv()
    result = json.loads(message) 
    server_version = result['d'].get('obsWebSocketVersion')
    auth = _build_auth_string(result['d']['authentication']['salt'], result['d']['authentication']['challenge'])

    payload = {
        "op": 1,
        "d": {
            "rpcVersion": 1,
            "authentication": auth,
            "eventSubscriptions": 1000 
        }
    }
    ws.send(json.dumps(payload))
    message = ws.recv()
    # Message Identified...or so we assume...probably good to check if this is empty or not.
    result = json.loads(message)
    print(result)

_auth()


# # shit worked, now lets change the scene cuz why not.
payload =  {"op": 6, "d": {"requestId": "SetMeSomeFrigginScenesYo", "requestType": "SetCurrentProgramScene", "requestData": {"sceneName":"AnotherSuperCoolScene"}}} #you could parse the GetSceneList and switch to one of those
ws.send(json.dumps(payload))
message=ws.recv()    
print(message)
while True:
    a = 1 + 1

ws.close()