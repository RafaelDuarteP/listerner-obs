import json


class StorageInterface:
    def __init__(self):
        self.storage_path = 'data.json'

    def load(self):
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return data['obs_host'], data['obs_port'], data['obs_password'], data['default_scene'], data['default_audio_source']
        except FileNotFoundError:
            return 'localhost', 4444, '', 'scene', 'Desktop Audio'
        
    def save(self, obs_host, obs_port, obs_password, default_scene, default_audio_source):
        data = {
            'obs_host': obs_host,
            'obs_port': obs_port,
            'obs_password': obs_password,
            'default_scene': default_scene,
            'default_audio_source': default_audio_source
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f)