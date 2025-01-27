import json
import uuid
import time


class OBSController:
    def __init__(
        self,
        obs_client,
        default_scene,
        default_audio_source,
        camera_id,
        previa_id,
        final_id,
        dizimo_id,
    ):
        self.obs_client = obs_client
        self.default_scene = default_scene
        self.default_audio_source = default_audio_source
        self.camera_id = camera_id
        self.previa_id = previa_id
        self.final_id = final_id
        self.dizimo_id = dizimo_id

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
                if result["d"]["requestStatus"]["code"] == 600:
                    print("Scene item not found.")
                    break
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

    def list_items(self):
        return self.obs_client.send_command(
            self.get_payload("GetSceneItemList", {"sceneName": self.default_scene})
        )

    def setup(self):
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.previa_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.camera_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.final_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.dizimo_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetInputMute",
                {
                    "inputName": self.default_audio_source,
                    "inputMuted": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetInputVolume",
                {
                    "inputName": self.default_audio_source,
                    "inputVolumeDb": 0,
                },
            )
        )
        self.transition("Cortar", 50)

    def iniciar(self):
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.previa_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.camera_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.final_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.dizimo_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetInputMute",
                {
                    "inputName": self.default_audio_source,
                    "inputMuted": False,
                },
            )
        )
        self.transition("Esmaecer", 800)

    def iniciar_dizimo(self):
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.previa_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.camera_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.final_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.dizimo_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetInputMute",
                {
                    "inputName": self.default_audio_source,
                    "inputMuted": False,
                },
            )
        )
        self.transition("Entrar", 1000)

    def finalizar_dizimo(self):
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.previa_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.camera_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.final_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.dizimo_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetInputMute",
                {
                    "inputName": self.default_audio_source,
                    "inputMuted": False,
                },
            )
        )
        self.transition("Sair", 1000)

    def finalizar(self):
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.previa_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.camera_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.final_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": True,
                },
            )
        )
        self.obs_client.send_command(
            self.get_payload(
                "SetSceneItemEnabled",
                {
                    "sceneItemId": self.dizimo_id,
                    "sceneName": self.default_scene,
                    "sceneItemEnabled": False,
                },
            )
        )
        self.transition("Esmaecer", 10000)
        inicio_db = 0
        fim_db = -50
        duracao = 15
        passos = 600
        intervalo = duracao / passos
        for i in range(passos + 1):
            volume_db = inicio_db + (fim_db - inicio_db) * (i / passos)
            self.obs_client.send_command(
                self.get_payload(
                    "SetInputVolume",
                    {
                        "inputName": self.default_audio_source,
                        "inputVolumeDb": volume_db,
                    },
                )
            )
            time.sleep(intervalo)
        self.stop()
