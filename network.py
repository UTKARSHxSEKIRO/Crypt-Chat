import socket, threading, queue

class HostServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', 5555))
        self.server.listen()
        self.clients = []
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            conn, addr = self.server.accept()
            self.clients.append(conn)
            threading.Thread(target=self.handle, args=(conn,), daemon=True).start()

    def handle(self, conn):
        while True:
            try:
                data = conn.recv(4096)
                if not data: break
                for c in self.clients:
                    if c != conn: c.sendall(data)
            except: break
        self.clients.remove(conn)
        conn.close()

class NetworkManager:
    def __init__(self, msg_queue):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = msg_queue

    def connect(self, host, port):
        self.sock.connect((host, int(port)))
        threading.Thread(target=self.listen, daemon=True).start()
        return True

    def listen(self):
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if data: self.queue.put(data)
            except: break

    def send(self, data): 
        self.sock.sendall(data.encode())