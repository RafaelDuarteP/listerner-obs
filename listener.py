import tkinter as tk
from tkinter import messagebox
import sys
import queue

from message_handler import MessageHandler
from obs_client import OBSWebSocketClient
from obs_controller import OBSController
from udp_listener import UDPListener
from storage_interface import StorageInterface
from datetime import datetime


class LogRedirector:
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, message):
        if message.strip():
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            self.log_queue.put(timestamp + message + "\n")

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
        self.root.geometry("600x600")
        self.root.title("OBS WebSocket Listener")

        header_frame = tk.Frame(root)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        tk.Label(header_frame, text="OBS WebSocket Listener").grid(row=0, column=0)
        self.status_canvas = tk.Canvas(
            header_frame, width=20, height=20, bg="white", highlightthickness=0
        )
        self.status_canvas.grid(row=0, column=1, padx=5)

        self.update_status_indicator("red")

        tk.Label(root, text="OBS Host:").grid(row=1, column=0, sticky="ew")
        tk.Label(root, text="OBS Port:").grid(row=2, column=0, sticky="ew")
        tk.Label(root, text="OBS Password:").grid(row=3, column=0, sticky="ew")
        tk.Label(root, text="Default Scene:").grid(row=4, column=0, sticky="ew")
        tk.Label(root, text="Default Audio Source:").grid(row=5, column=0, sticky="ew")

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

        self.obs_host.grid(row=1, column=1, sticky="ew")
        self.obs_port.grid(row=2, column=1, sticky="ew")
        self.obs_password.grid(row=3, column=1, sticky="ew")
        self.default_scene.grid(row=4, column=1, sticky="ew")
        self.default_audio_source.grid(row=5, column=1, sticky="ew")

        # Botões
        self.start_button = tk.Button(
            root, text="Start Listener", command=self.start_listener
        )
        self.start_button.grid(row=6, column=0, sticky="ew")

        self.stop_button = tk.Button(
            root, text="Stop Listener", command=self.stop_listener
        )
        self.stop_button.grid(row=6, column=1, sticky="ew")
        self.stop_button.config(state=tk.DISABLED)

        self.restart_button = tk.Button(
            root, text="Restart Listener", command=self.restart_listener
        )
        self.restart_button.grid(row=7, columnspan=2, sticky="ew")
        self.restart_button.config(state=tk.DISABLED)

        # Log
        self.log_text = tk.Text(
            root, height=20, width=50, bg="black", fg="white", font=("Courier", 10)
        )
        self.log_text.grid(row=8, column=0, columnspan=2, sticky="nsew")

        self.clear_log_button = tk.Button(root, text="Clear Log", command=self.clear_log)
        self.clear_log_button.grid(row=9, columnspan=2, sticky="ew", pady=5)


        self.log_queue = queue.Queue()
        sys.stdout = LogRedirector(self.log_queue)

        self.process_log_queue()

        for i in range(8):
            root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def update_status_indicator(self, color):
        self.status_canvas.delete("all")
        self.status_canvas.create_oval(2, 2, 18, 18, fill=color)

    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

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

        host = self.obs_host.get().strip()
        port = self.obs_port.get().strip()
        password = self.obs_password.get()
        scene = self.default_scene.get().strip()
        audio_source = self.default_audio_source.get().strip()

        if (
            not host
            or not port.isdigit()
            or not password
            or not scene
            or not audio_source
        ):
            messagebox.showerror(
                "Error", "All fields are required and port must be a number."
            )
            return

        self.storage_interface.save(host, port, password, scene, audio_source)

        try:
            port = int(port)  # Port convertido após validação
            self.obs_client = OBSWebSocketClient(host, port, password)
            self.obs_client.connect()
            self.obs_client.authenticate()

            controller = OBSController(self.obs_client, scene, audio_source)
            message_handler = MessageHandler(controller)

            self.listener = UDPListener("0.0.0.0", 12345, message_handler.handle)
            self.listener.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)

            print("Listener started successfully.")
            self.show_message("Info", "Listener started successfully.")
            self.update_status_indicator("green")
        except Exception as e:
            print(f"Failed to start listener: {e}")
            self.show_message("Error", f"Failed to start listener: {e}")

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.obs_client.close()
            self.obs_client = None

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)

            print("Listener stopped successfully.")
            self.show_message("Info", "Listener stopped successfully.")
            self.update_status_indicator("red")
        else:
            print("No listener is running.")
            self.show_message("Warning", "No listener is running.")

    def restart_listener(self):
        print("Restarting listener...")
        self.stop_listener()
        self.start_listener()

    def on_close(self):
        if self.listener:
            self.listener.stop()
        self.root.destroy()

    def show_message(self, title, message):
        self.root.after(0, lambda: messagebox.showinfo(title, message))


if __name__ == "__main__":
    root = tk.Tk()
    app = ListenerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Associa o evento de fechar janela
    root.mainloop()
