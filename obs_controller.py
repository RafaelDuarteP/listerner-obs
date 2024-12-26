import uuid


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
