import socket, threading
clients = []

def handle(conn):
    clients.append(conn)
    while True:
        try:
            data = conn.recv(4096)
            if not data: break
            for c in clients:
                if c != conn: c.sendall(data)
        except: break
    clients.remove(conn); conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen()
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()