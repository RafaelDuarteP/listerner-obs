import select
import socket
from threading import Thread


class UDPListener:
    def __init__(self, ip, port, handler):
        self.ip = ip
        self.port = port
        self.handler = handler
        self.running = False
        self.thread = None
        self.sock = None

    def start(self):
        self.running = True
        self.thread = Thread(target=self._listen)
        self.thread.start()

    def stop(self):
        print("Stopping UDP listener...")
        self.running = False
        if self.sock:
            self.sock.close()  # Fecha o socket para desbloquear `recvfrom`
        if self.thread:
            self.thread.join()

    def _listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.setblocking(False)  # Torna o socket não bloqueante
        print(f"UDP listener started on {self.ip}:{self.port}")

        while self.running:
            ready = select.select([self.sock], [], [], 0.5)  # Timeout de 0.5s
            if ready[0]:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    self.handler(data)
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
        self.sock.close()
        print("UDP listener stopped.")
