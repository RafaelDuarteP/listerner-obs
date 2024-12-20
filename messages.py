payload_mute = {
    "op": 6,
    "d": {
        "requestId": "SetMeSomeFrigginScenesYo",
        "requestType": "ToggleInputMute",
        "requestData": {"inputName": "Mic/Aux"},
    },
}




def getPayload(data):
    match data:
        case b"mute":
            return payload_mute
        case _:
            return False
