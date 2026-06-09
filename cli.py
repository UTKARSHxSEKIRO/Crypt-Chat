import threading
import time
import queue
import json
import os
import sys
import logic
from network import NetworkManager

def listen_to_queue(msg_queue, password):
    """Background thread to capture, decrypt, and display incoming structured payloads."""
    cache_dir = "received_files_cli"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    while True:
        try:
            raw_payload = msg_queue.get_nowait()
            decrypted_json = logic.decrypt(raw_payload, password)
            
            # Unpack the structured JSON packet protocol
            packet = json.loads(decrypted_json)
            data_type = packet.get("type")
            
            # Reposition terminal cursor dynamically to prevent incoming text from breaking active typing
            print("\r", end="", flush=True)
            
            if data_type == "text":
                text_content = packet.get("content")
                print(f"Peer: {text_content}")
                
            elif data_type == "file":
                filename = packet.get("filename")
                base64_content = packet.get("content")
                
                output_path = os.path.join(cache_dir, filename)
                logic.decode_base64_to_file(base64_content, output_path)
                print(f"📦 Peer sent file (Saved to {output_path}): {filename}")

            # Restore the input line prompt cleanly
            print("You: ", end="", flush=True)
        except queue.Empty:
            pass
        except Exception as e:
            # Silently catch structural/malformed anomalies or handle stream drops
            pass
            
        time.sleep(0.1)

def run_cli():
    msg_queue = queue.Queue()
    net = NetworkManager(msg_queue)
    
    print("\n=========================================")
    print("      CRYPT-CHAT ADVANCED CORE CLI       ")
    print("=========================================")
    role = input("Choose Role - [H]ost (Server) or [G]uest (Client): ").strip().lower()
    
    if role == 'h':
        # Feature Parity: Max Room Capacity Input
        try:
            max_users = int(input("Set Maximum Room Capacity (Default 5): ").strip() or "5")
        except ValueError:
            print("[Config] Invalid number. Falling back to 5 slots.")
            max_users = 5

        # Feature Parity: Custom Key File Export Location
        save_dir = input("Enter directory path to export KEY.json (Press Enter for current directory): ").strip() or "."
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                print(f"Error creating directory: {e}. Falling back to current folder.")
                save_dir = "."
        
        target_key_path = os.path.join(save_dir, "KEY.json")
        
        password = logic.generate_password().strip()
        print("\n=========================================")
        print(f"🔑 ROOM PASSWORD: {password}")
        print(f"📁 KEY ASSET EXPORTED TO: {target_key_path}")
        print("=========================================")
        
        # Initialize key file generation
        logic.create_key_file(target_key_path)
        
        # Fire up the multi-client network architecture passing limits down to sockets
        net.start_as_host(port=5555, max_users=max_users)
        print("\n[System] TCP Socket listening engine active on port 5555.")
        print("[System] Start your zrok private share tunnel now.")
        input("--> Press [Enter] once your zrok tunnel is live to open the chatroom...")

    elif role == 'g':
        password = input("Enter the 25-character room password: ").strip()
        host = input("Zrok Local Host (Default 127.0.0.1): ").strip() or "127.0.0.1"
        port = input("Zrok Local Access Port (e.g., 9191): ").strip()
        
        if not port:
            print("[Error] Local access routing proxy port is required.")
            return
            
        print("\n[Network] Tunneling connection handle over socket...")
        try:
            net.connect_as_guest(host, int(port))
            print("[Network] Connection successfully verified.")
        except Exception as e:
            print(f"[Network Error] Connection refused: {e}")
            return
    else:
        print("[Error] Invalid operational choice. Terminating.")
        return

    # Start the asynchronous, non-blocking background consumer loop thread
    listener = threading.Thread(target=listen_to_queue, args=(msg_queue, password), daemon=True)
    listener.start()

    print("\n======================================================================")
    print(" Secure Portal Fully Active.")
    print(" Commands: /peers (View room users) | /file <path> (Send files) | /exit")
    print("======================================================================")
    
    while True:
        try:
            msg = input("You: ").strip()
            if not msg:
                continue
                
            if msg.lower() == '/exit':
                print("[System] Dropping network handles and exiting.")
                break
            
            # Feature Parity: Real-Time Active Connection Listing Command
            if msg.lower() == '/peers':
                print("\n--- ACTIVE ROOM PARTICIPANTS ---")
                if net.is_host:
                    print(f"Role: Host | Capacity Tracker: {len(net.clients)}/{net.max_users}")
                    for i, client_sock in enumerate(net.clients, start=1):
                        try:
                            addr = client_sock.getpeername()
                            print(f" [{i}] Peer Address Handle: {addr[0]}:{addr[1]}")
                        except:
                            print(f" [{i}] Unknown or Disconnecting Endpoint")
                else:
                    print("Role: Guest Node")
                    print(f"Connected Tunnel Path Target -> {host}:{port}")
                print("--------------------------------")
                continue
                
            # Feature Parity: Binary File / Image Transfer Parser Command
            if msg.startswith('/file '):
                file_path = msg.replace('/file ', '', 1).strip()
                if not os.path.exists(file_path):
                    print(f"[File Error] Resource artifact not located at: '{file_path}'")
                    continue
                    
                filename = os.path.basename(file_path)
                print(f"[Encoding] Converting binary stream for: {filename}...")
                
                base64_content = logic.encode_file_to_base64(file_path)
                packet = {"type": "file", "filename": filename, "content": base64_content}
                print("[Network] Dispatching encrypted hex payload package...")
                
            else:
                # Standard Text Package Payload Wrapping Protocol Configuration
                packet = {"type": "text", "content": msg}

            serialized_packet = json.dumps(packet)
            encrypted_payload = logic.encrypt(serialized_packet, password)
            net.net.send_message(encrypted_payload) if hasattr(net, 'net') else net.send_message(encrypted_payload)
            
        except (KeyboardInterrupt, EOFError):
            print("\n[System] Terminal break signal intercepted. Shutting down pipeline channels.")
            break