import threading
import time
import queue
import logic
from network import NetworkManager, HostServer

def listen_to_queue(msg_queue, password):
    """Background thread to process and print incoming network payloads."""
    while True:
        try:
            raw_msg = msg_queue.get_nowait()
            decrypted = logic.decrypt(raw_msg, password)
            
            # Print incoming data structure cleanly to the terminal stream
            print(f"\n[INCOMING RAW]: {raw_msg[:20]}...")
            print(f"Peer: {decrypted}")
            print("You: ", end="", flush=True)
        except queue.Empty:
            pass
        time.sleep(0.1)

def run_cli():
    msg_queue = queue.Queue()
    net = NetworkManager(msg_queue)
    
    print("\n=== Crypt-Chat CLI ===")
    role = input("Choose Role - [S]ender (Host) or [R]eceiver: ").strip().lower()
    
    if role == 's':
        password = logic.generate_password().strip()
        print(f"\nGenerated Security Password: {password}")
        
        # Automate key asset configuration locally
        logic.create_key_file("KEY.json")
        print("KEY.json created automatically in current directory.")
        print("\nStarting background zrok server target on Port 5555...")
        
        background_server = HostServer()
        net.connect('127.0.0.1', 5555)
        print("Server initialization complete. Initialize zrok share tunnel now.")
        input("Press [Enter] once your peer connects to start chatting...")

    elif role == 'r':
        key_path = input("Path to KEY.json (Default: ./KEY.json): ").strip() or "KEY.json"
        if not logic.verify_key_file(key_path):
            print("Invalid KEY.json configuration. Terminating session.")
            return
            
        password = input("Enter the 25-character password: ").strip()
        host = input("Zrok Host IP/Domain (e.g., 127.0.0.1): ").strip()
        port = input("Zrok Port (e.g., 9191): ").strip()
        
        print("\nEstablishing socket connection across tunnel...")
        try:
            net.connect(host, int(port))
            print("Connection successfully established.")
        except Exception as e:
            print(f"Network error encountered: {e}")
            return
    else:
        print("Invalid operational role selected. Terminating.")
        return

    # Initialize concurrent daemon thread for message polling
    listener = threading.Thread(target=listen_to_queue, args=(msg_queue, password), daemon=True)
    listener.start()

    print("\n--- Secure Session Established. Type messages below ---")
    while True:
        try:
            msg = input("You: ").strip()
            if msg.lower() == '/exit':
                print("Closing local network handles.")
                break
            if msg:
                encrypted = logic.encrypt(msg, password)
                net.send(encrypted)
                print(f"[OUTGOING RAW]: {encrypted[:20]}...")
        except (KeyboardInterrupt, EOFError):
            print("\nSession terminated by system interrupt.")
            break