import tkinter as tk
from tkinter import messagebox, Toplevel

class ConfigPopup:
    def __init__(self, parent, storage_interface):
        self.window = Toplevel(parent)
        self.window.title("Configurar Entradas")
        self.window.geometry("350x400")
        self.entries = {}
        self.storage = storage_interface

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
        saved = self.storage.load()

        for idx, label in enumerate(labels):
            tk.Label(self.window, text=label).grid(row=idx, column=0, sticky="e")
            entry = tk.Entry(self.window, show="*" if "Password" in label else "")
            entry.insert(0, saved[idx])
            entry.grid(row=idx, column=1, columnspan=2, sticky="ew")
            self.entries[label] = entry

        save_btn = tk.Button(self.window, text="Salvar", command=self.save_config)
        save_btn.grid(row=len(labels), columnspan=3, pady=10)

    def save_config(self):
        values = [e.get().strip() for e in self.entries.values()]
        if not all(values) or not values[1].isdigit():
            messagebox.showerror(
                "Erro", "Todos os campos são obrigatórios e a porta deve ser numérica."
            )
            return
        self.storage.save(*values)
        messagebox.showinfo("Salvo", "Configurações salvas.")
        self.window.destroy()
