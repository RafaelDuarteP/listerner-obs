import tkinter as tk
from tkinter import messagebox
import sys
import queue

from message_handler import MessageHandler
from obs_client import OBSWebSocketClient
from obs_controller import OBSController
from udp_listener import UDPListener
from storage_interface import StorageInterface


class LogRedirector:
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, message):
        if message.strip():
            self.log_queue.put(message + "\n")

    def flush(self):
        pass


class ListenerApp:
    def __init__(self, root):
        self.storage_interface = StorageInterface()
        self.root = root
        self.listener = None

        obs_host, obs_port, obs_password, default_scene, default_audio_source = (
            self.storage_interface.load()
        )

        self.root.title("OBS WebSocket Listener")

        tk.Label(root, text="OBS Host:").grid(row=0, column=0)
        tk.Label(root, text="OBS Port:").grid(row=1, column=0)
        tk.Label(root, text="OBS Password:").grid(row=2, column=0)
        tk.Label(root, text="Default Scene:").grid(row=3, column=0)
        tk.Label(root, text="Default Audio Source:").grid(row=4, column=0)

        self.obs_host = tk.Entry(root)
        self.obs_host.insert(0, obs_host)
        self.obs_port = tk.Entry(root)
        self.obs_port.insert(0, obs_port)
        self.obs_password = tk.Entry(root, show="*")
        self.obs_password.insert(0, obs_password)
        self.default_scene = tk.Entry(root)
        self.default_scene.insert(0, default_scene)
        self.default_audio_source = tk.Entry(root)
        self.default_audio_source.insert(0, default_audio_source)

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

        self.log_text = tk.Text(
            root, height=10, width=50, bg="black", fg="white", font=("Courier", 10)
        )
        self.log_text.grid(row=6, column=0, columnspan=2)

        self.log_queue = queue.Queue()

        sys.stdout = LogRedirector(self.log_queue)

        self.process_log_queue()

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.yview(tk.END)
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)

    def start_listener(self):
        if self.listener:
            messagebox.showwarning("Warning", "Listener is already running.")
            return

        host = self.obs_host.get()
        port = int(self.obs_port.get())
        password = self.obs_password.get()
        scene = self.default_scene.get()
        audio_source = self.default_audio_source.get()

        self.storage_interface.save(host, port, password, scene, audio_source)

        try:
            obs_client = OBSWebSocketClient(host, port, password)
            obs_client.connect()
            obs_client.authenticate()

            controller = OBSController(obs_client, scene, audio_source)
            message_handler = MessageHandler(controller)

            self.listener = UDPListener("0.0.0.0", 12345, message_handler.handle)
            self.listener.start()

            print("Listener started successfully.")
            self.show_message("Info", "Listener started successfully.")
        except Exception as e:
            print(f"Failed to start listener: {e}")
            self.show_message("Error", f"Failed to start listener: {e}")

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Listener stopped successfully.")
            self.show_message("Info", "Listener stopped successfully.")
        else:
            print("No listener is running.")
            self.show_message("Warning", "No listener is running.")

    def show_message(self, title, message):
        self.root.after(0, lambda: messagebox.showinfo(title, message))


if __name__ == "__main__":
    root = tk.Tk()
    app = ListenerApp(root)
    root.mainloop()
