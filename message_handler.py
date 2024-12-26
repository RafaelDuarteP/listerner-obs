import re


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

        elif message == "listItems":
            try:
                items = self.controller.list_items()
                print("Listed items.")
                scene_items = items["d"]["responseData"]["sceneItems"]
                for item in scene_items:
                    print(f"{'{'}sourceName: {item['sourceName']}, sceneItemId: {item['sceneItemId']}{'}'}")
            except Exception as e:
                print(f"An error occurred: {e}")
