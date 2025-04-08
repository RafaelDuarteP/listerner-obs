from app.listener_app import ListenerApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = ListenerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
