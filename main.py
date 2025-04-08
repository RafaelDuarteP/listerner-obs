import tkinter as tk

from listener_app import ListenerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ListenerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
