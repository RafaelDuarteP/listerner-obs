import socket
import websocket
import json
import signal
import sys
import hashlib
import base64
import messages as m

udp_ip = "0.0.0.0"
udp_port = 5005

obs_host = "localhost"
obs_port = 4455
obs_password = "Iw5ja6Pxv6TkJICO"
obs_url = "ws://{}:{}".format(obs_host, obs_port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ws = websocket.WebSocket()


def _signal_handler(sig, frame):
    print("\nGracefully stopping...")
    sock.close()
    print("UDP socket closed")
    ws.close()
    print("Websocket closed")
    sys.exit(0)


def _build_auth_string(salt, challenge):
    secret = base64.b64encode(
        hashlib.sha256((obs_password + salt).encode("utf-8")).digest()
    )
    auth = base64.b64encode(
        hashlib.sha256(secret + challenge.encode("utf-8")).digest()
    ).decode("utf-8")
    return auth


def _auth():
    message = ws.recv()
    result = json.loads(message)
    server_version = result["d"].get("obsWebSocketVersion")
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
    return result

def _connect():
    ws.close()
    ws.connect(obs_url)
    response = _auth()
    print("Websocket connection established", response)


def main():
    sock.bind((udp_ip, udp_port))
    print("UDP socket started successfully")

    _connect()

    signal.signal(
        signal.SIGINT,
        _signal_handler,
    )

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received message: {data}")
        try:
            payload = m.getPayload(data) 
            if not payload:
                continue
            print(f"Sending payload: {payload}")
            ws.send(json.dumps(payload))
            message = ws.recv()
            print(json.loads(message))
        except Exception as e:
            print(f"Error: {e}")
            _connect()
            continue


if __name__ == "__main__":
    main()
