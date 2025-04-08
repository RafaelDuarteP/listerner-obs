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
