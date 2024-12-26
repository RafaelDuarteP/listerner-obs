import tkinter as tk
from tkinter import messagebox

from message_handler import MessageHandler
from obs_client import OBSWebSocketClient
from obs_controller import OBSController
from udp_listener import UDPListener
class ListenerApp:
    def __init__(self, root):
        self.root = root
        self.listener = None

        self.root.title("OBS WebSocket Listener")

        tk.Label(root, text="OBS Host:").grid(row=0, column=0)
        tk.Label(root, text="OBS Port:").grid(row=1, column=0)
        tk.Label(root, text="OBS Password:").grid(row=2, column=0)
        tk.Label(root, text="Default Scene:").grid(row=3, column=0)
        tk.Label(root, text="Default Audio Source:").grid(row=4, column=0)

        self.obs_host = tk.Entry(root)
        self.obs_port = tk.Entry(root)
        self.obs_password = tk.Entry(root, show="*")
        self.default_scene = tk.Entry(root)
        self.default_audio_source = tk.Entry(root)

        self.obs_host.grid(row=0, column=1)
        self.obs_port.grid(row=1, column=1)
        self.obs_password.grid(row=2, column=1)
        self.default_scene.grid(row=3, column=1)
        self.default_audio_source.grid(row=4, column=1)

        tk.Button(root, text="Start Listener", command=self.start_listener).grid(
            row=5, column=0
        )
        tk.Button(root, text="Stop Listener", command=self.stop_listener).grid(
            row=5, column=1
        )

    def start_listener(self):
        if self.listener:
            messagebox.showwarning("Warning", "Listener is already running.")
            return

        host = self.obs_host.get() or "localhost"
        port = int(self.obs_port.get() or 4455)
        password = self.obs_password.get()
        scene = self.default_scene.get() or "tela"
        audio_source = self.default_audio_source.get() or "Desktop Audio"

        try:
            obs_client = OBSWebSocketClient(host, port, password)
            obs_client.connect()
            obs_client.authenticate()

            controller = OBSController(obs_client, scene, audio_source)
            message_handler = MessageHandler(controller)

            self.listener = UDPListener("0.0.0.0", 12345, message_handler.handle)
            self.listener.start()

            messagebox.showinfo("Info", "Listener started successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start listener: {e}")

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            messagebox.showinfo("Info", "Listener stopped successfully.")
        else:
            messagebox.showwarning("Warning", "No listener is running.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ListenerApp(root)
    root.mainloop()
