import socket
import threading
import queue

class NetworkManager:
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.sock = None
        self.is_host = False
        self.max_users = 5
        self.clients = []  # Track active peer socket handles

    def start_as_host(self, port=5555, max_users=5):
        """Initializes the master listening socket for the chatroom."""
        self.is_host = True
        self.max_users = max_users
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', port))
        server.listen()
        
        # Run acceptance engine asynchronously to prevent interface hanging
        threading.Thread(target=self._accept_connections, args=(server,), daemon=True).start()

    def _accept_connections(self, server):
        while True:
            try:
                client_sock, client_addr = server.accept()
                
                # Enforce capacity verification bounds before saving context
                if len(self.clients) >= self.max_users:
                    print(f"[System Info] Connection rejected from {client_addr} - Capacity full.")
                    client_sock.close()
                    continue
                
                self.clients.append(client_sock)
                print(f"[System] Connected handle registered from {client_addr}")
                
                # Delegate continuous packet sniffing to an isolated daemon thread
                threading.Thread(target=self._listen_to_client, args=(client_sock,), daemon=True).start()
            except Exception as e:
                print(f"[Network Error] Acceptance exception: {e}")
                break

    def _listen_to_client(self, client_sock):
        """Asynchronous data collection handler running per client link."""
        while True:
            try:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                # Push payload upstream to the host system queue
                self.msg_queue.put(data)
                
                # Distribute payload out to all companion connected nodes
                self._broadcast(data, exclude_sock=client_sock)
            except:
                break
        
        # Clean array space when thread disconnect conditions hit
        if client_sock in self.clients:
            self.clients.remove(client_sock)
        client_sock.close()

    def _broadcast(self, data, exclude_sock):
        """Dispatches encrypted payload data packets down remaining open conduits."""
        for client in self.clients:
            if client != exclude_sock:
                try:
                    client.sendall(data)
                except:
                    client.close()
                    if client in self.clients:
                        self.clients.remove(client)

    def connect_as_guest(self, host, port):
        """Establishes connection endpoints to the host's tunnel loop."""
        self.is_host = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        
        threading.Thread(target=self._listen_to_server, daemon=True).start()

    def _listen_to_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self.msg_queue.put(data)
            except:
                print("[Network Info] Connection link severed by host.")
                break

    def send_message(self, data_bytes):
        """Entry execution path to write data frames over active channels."""
        if self.is_host:
            self._broadcast(data_bytes, exclude_sock=None)
        else:
            if self.sock:
                try:
                    self.sock.sendall(data_bytes)
                except Exception as e:
                    print(f"[Network Error] Data transit fault: {e}")