import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class Watcher:
    DIRECTORY_TO_WATCH = "./"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type in ('created', 'modified'):
            # Reinicia o listener.py quando um arquivo é criado ou modificado
            print(f"Received {event.event_type} event - {event.src_path}")
            subprocess.run(["pkill", "-f", "listener.py"])  # Mata o processo listener.py se estiver rodando
            subprocess.run(["python3", "listener.py"])  # Reinicia o listener.py

if __name__ == '__main__':
    w = Watcher()
    w.run()