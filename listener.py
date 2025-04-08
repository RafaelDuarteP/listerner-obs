import tkinter as tk
from tkinter import messagebox, Menu, Toplevel
import sys
import queue
from datetime import datetime

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
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            self.log_queue.put(timestamp + message + "\n")

    def flush(self):
        pass


class ListenerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x600")
        self.root.title("OBS WebSocket Listener")
        self.listener = None
        self.obs_client = None
        self.storage_interface = StorageInterface()
        self.log_queue = queue.Queue()

        self.build_menu()
        self.build_main_ui()

        sys.stdout = LogRedirector(self.log_queue)
        self.process_log_queue()

    def build_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Configurar Entradas", command=self.show_config_popup)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Comandos Disponíveis", command=self.show_command_docs)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

    def build_main_ui(self):
        header = tk.Frame(self.root)
        header.pack(pady=10)

        tk.Label(header, text="OBS WebSocket Listener").pack(side=tk.LEFT)
        self.status_canvas = tk.Canvas(
            header, width=20, height=20, bg="white", highlightthickness=0
        )
        self.status_canvas.pack(side=tk.LEFT, padx=10)
        self.update_status_indicator("red")

        # Botões
        self.start_button = tk.Button(
            self.root, text="Iniciar o Listener", command=self.start_listener
        )
        self.start_button.pack(fill=tk.X, padx=10)

        self.stop_button = tk.Button(
            self.root,
            text="Parar o Listener",
            command=self.stop_listener,
            state=tk.DISABLED,
        )
        self.stop_button.pack(fill=tk.X, padx=10)

        self.restart_button = tk.Button(
            self.root,
            text="Reiniciar o Listener",
            command=self.restart_listener,
            state=tk.DISABLED,
        )
        self.restart_button.pack(fill=tk.X, padx=10)

        # Log
        self.log_text = tk.Text(
            self.root, height=20, bg="black", fg="white", font=("Courier", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.clear_log_button = tk.Button(
            self.root, text="Clear Log", command=self.clear_log
        )
        self.clear_log_button.pack(fill=tk.X, padx=10, pady=(0, 10))

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

    def show_config_popup(self):
        config_window = Toplevel(self.root)
        config_window.title("Configurar Entradas")
        config_window.geometry("350x400")

        labels = [
            "OBS Host",
            "OBS Port",
            "OBS Password",
            "Default Scene",
            "Default Audio Source",
            "Camera id",
            "Previa id",
            "Final id",
            "Dizimo id",
        ]
        self.entries = {}
        saved = self.storage_interface.load()

        for idx, label in enumerate(labels):
            tk.Label(config_window, text=label).grid(row=idx, column=0, sticky="e")
            entry = tk.Entry(config_window, show="*" if "Password" in label else "")
            entry.insert(0, saved[idx])
            entry.grid(row=idx, column=1, columnspan=2, sticky="ew")
            self.entries[label] = entry

        def save_config():
            values = [e.get().strip() for e in self.entries.values()]
            if not all(values) or not values[1].isdigit():
                messagebox.showerror(
                    "Erro",
                    "Todos os campos são obrigatórios e a porta deve ser numérica.",
                )
                return
            self.storage_interface.save(*values)
            messagebox.showinfo("Salvo", "Configurações salvas.")
            config_window.destroy()

        save_btn = tk.Button(config_window, text="Salvar", command=save_config)
        save_btn.grid(row=len(labels), columnspan=3, pady=10)

    def show_command_docs(self):
        doc = """
    Comandos que o Listener aceita via UDP:

    • toggleItem<ID>
    - Alterna visibilidade de um item na cena principal pela ID. Ex: toggleItem42

    • transition<NOME><DURAÇÃO>
    - Faz transição com nome e duração. Ex: transitionfade1000

    • scene <nome> <transição> <duração> <mute> <fadeOut> <volume>
    - Troca para uma cena com parâmetros opcionais. Ex: scene Cena1 fade 1000 true true 70

    • toggleMute
    - Alterna o mute da fonte de áudio padrão

    • startRecord
    - Inicia gravação

    • startLive
    - Inicia transmissão ao vivo

    • stop
    - Encerra gravação e transmissão

    • setup
    - Executa setup inicial

    • iniciar
    - Inicia transmissão padrão

    • iniciarDizimo
    - Inicia modo dízimo

    • finalizarDizimo
    - Finaliza modo dízimo

    • finalizar
    - Finaliza transmissão

    • listItems
    - Lista os itens da cena atual com sourceName e sceneItemId
    """
        top = tk.Toplevel(self.root)
        top.title("Comandos Disponíveis")
        top.geometry("600x500")
        top.transient(self.root)
        top.grab_set()

        text = tk.Text(top, wrap="word", bg="black", fg="white", font=("Courier", 10))
        text.insert(tk.END, doc)
        text.config(state="disabled")
        text.pack(expand=True, fill="both")


    def start_listener(self):
        if self.listener:
            messagebox.showwarning("Aviso", "Listener já está em execução.")
            return

        try:
            (
                host,
                port,
                password,
                scene,
                audio_source,
                camera_id,
                previa_id,
                final_id,
                dizimo_id,
            ) = self.storage_interface.load()
            port = int(port)

            self.obs_client = OBSWebSocketClient(host, port, password)
            self.obs_client.connect()
            self.obs_client.authenticate()

            controller = OBSController(
                self.obs_client,
                scene,
                audio_source,
                int(camera_id),
                int(previa_id),
                int(final_id),
                int(dizimo_id),
            )
            message_handler = MessageHandler(controller)

            self.listener = UDPListener("0.0.0.0", 12345, message_handler.handle)
            self.listener.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.update_status_indicator("green")
            print("Listener started.")
        except Exception as e:
            print(f"Erro ao iniciar o listener: {e}")
            self.show_message("Erro", str(e))

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            if self.obs_client:
                self.obs_client.close()
                self.obs_client = None

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.update_status_indicator("red")
            print("Listener parado.")
        else:
            print("Nenhum listener em execução.")

    def restart_listener(self):
        print("Reiniciando listener...")
        self.stop_listener()
        self.start_listener()

    def show_message(self, title, message):
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def on_close(self):
        if self.listener:
            self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ListenerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
