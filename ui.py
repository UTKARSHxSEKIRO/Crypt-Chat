import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk  # Ensure 'pillow' is installed in your venv
import queue
import os
import json
import logic
from network import NetworkManager

class CryptChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypt-Chat Multi-User Portal")
        self.root.geometry("850x600")
        self.root.minsize(850, 600)
        
        self.msg_queue = queue.Queue()
        self.net = NetworkManager(self.msg_queue)
        self.password = ""
        self.max_users = 5  
        
        # Ensure a local directory exists to save incoming file transfers cleanly
        self.cache_dir = "received_files"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # To keep reference of loaded images so garbage collection doesn't delete them
        self.loaded_images = []

        self._build_welcome_screen()

    def _build_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(pady=80)

        tk.Label(self.welcome_frame, text="Crypt-Chat Advanced Router", font=("Arial", 16, "bold")).pack(pady=15)
        
        tk.Button(self.welcome_frame, text="Host a New Chatroom", width=25, command=self._setup_capacity_screen).pack(pady=5)
        tk.Button(self.welcome_frame, text="Join an Existing Room", width=25, command=self._setup_guest_workflow).pack(pady=5)

    def _setup_capacity_screen(self):
        self.welcome_frame.pack_forget()
        
        self.config_frame = tk.Frame(self.root)
        self.config_frame.pack(pady=50)
        
        tk.Label(self.config_frame, text="Room Configuration Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.config_frame, text="Maximum Number of Allowed Participants:").pack()
        self.capacity_entry = tk.Entry(self.config_frame, width=10, justify="center")
        self.capacity_entry.insert(0, "5")
        self.capacity_entry.pack(pady=5)
        
        tk.Button(self.config_frame, text="Initialize Server Engine", command=self._process_host_initialization).pack(pady=15)

    def _process_host_initialization(self):
        try:
            self.max_users = int(self.capacity_entry.get().strip())
        except ValueError:
            messagebox.showerror("Configuration Error", "Please input a valid integer for capacity limitations.")
            return

        save_dir = filedialog.askdirectory(title="Select Directory to Export Security Key File")
        if not save_dir:
            messagebox.showwarning("Directory Required", "You must choose a location to export the key structure configuration.")
            return

        target_key_path = os.path.join(save_dir, "KEY.json")
        self.config_frame.pack_forget()
        
        self.password = logic.generate_password().strip()
        logic.create_key_file(target_key_path)
        
        self.net.start_as_host(port=5555, max_users=self.max_users)
        
        self.host_info_frame = tk.Frame(self.root)
        self.host_info_frame.pack(pady=40)
        
        tk.Label(self.host_info_frame, text="Room Initialization Complete", font=("Arial", 14, "bold"), fg="green").pack(pady=5)
        
        pwd_container = tk.Frame(self.host_info_frame)
        pwd_container.pack(pady=10)
        tk.Label(pwd_container, text=f"Room Password: {self.password}", font=("Arial", 11, "bold"), bg="#e1e1e1", padx=10, pady=5).pack(side=tk.LEFT)
        tk.Button(pwd_container, text="📋 Copy", command=self._copy_password_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.host_info_frame, text=f"Key Asset Exported To: {target_key_path}", font=("Arial", 9, "italic")).pack(pady=5)
        tk.Label(self.host_info_frame, text=f"Configured Room Capacity: {self.max_users} users").pack()
        tk.Label(self.host_info_frame, text="\nStep 1: Execute your zrok private share tunnel targeting local port 5555").pack()
        tk.Label(self.host_info_frame, text="Step 2: Provide the generated network credentials to your peers").pack()
        
        tk.Button(self.host_info_frame, text="Enter Active Chatroom View", width=30, command=self._build_chat_interface).pack(pady=25)

    def _copy_password_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.password)
        self.root.update()

    def _setup_guest_workflow(self):
        self.welcome_frame.pack_forget()
        
        self.guest_frame = tk.Frame(self.root)
        self.guest_frame.pack(pady=40)
        
        tk.Label(self.guest_frame, text="Enter Connection Parameters", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.guest_frame, text="Target Room Password:").pack()
        self.pwd_entry = tk.Entry(self.guest_frame, width=35)
        self.pwd_entry.pack(pady=2)
        
        tk.Label(self.guest_frame, text="Zrok Local Host (e.g., 127.0.0.1):").pack()
        self.host_entry = tk.Entry(self.guest_frame, width=35)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(pady=2)
        
        tk.Label(self.guest_frame, text="Zrok Local Access Port:").pack()
        self.port_entry = tk.Entry(self.guest_frame, width=35)
        self.port_entry.pack(pady=2)
        
        tk.Button(self.guest_frame, text="Establish Connection", command=self._connect_guest).pack(pady=15)

    def _connect_guest(self):
        self.password = self.pwd_entry.get().strip()
        host = self.host_entry.get().strip()
        port = int(self.port_entry.get().strip())
        
        try:
            self.net.connect_as_guest(host, port)
            self.guest_frame.pack_forget()
            self._build_chat_interface()
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Network connection refused: {e}")

    def _build_chat_interface(self):
        if hasattr(self, 'host_info_frame'):
            self.host_info_frame.pack_forget()

        self.sidebar_panel = tk.Frame(self.root, width=220, bg="#1e1e24", bd=2, relief=tk.SUNKEN)
        self.sidebar_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_panel.pack_propagate(False) 
        
        tk.Label(self.sidebar_panel, text="ACTIVE PEERS", font=("Arial", 11, "bold"), bg="#1e1e24", fg="#ffffff").pack(pady=10)
        
        self.peer_listbox = tk.Listbox(self.sidebar_panel, bg="#121214", fg="#00ff00", font=("Courier", 9), bd=0, highlightthickness=0)
        self.peer_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if self.net.is_host:
            self.peer_listbox.insert(tk.END, "[System] Role: Host")
            self.peer_listbox.insert(tk.END, f"[Limit]: Max {self.max_users}")
            self.peer_listbox.insert(tk.END, "--------------------")
        else:
            self.peer_listbox.insert(tk.END, "[System] Role: Guest")
            self.peer_listbox.insert(tk.END, "--------------------")

        self.main_chat_container = tk.Frame(self.root)
        self.main_chat_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(self.main_chat_container, height=18, width=60)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(self.main_chat_container, text="Network Payload Stream (Encrypted Traffic Log):", font=("Arial", 9, "gray")).pack(anchor=tk.W)
        self.log_display = scrolledtext.ScrolledText(self.main_chat_container, height=6, width=60, fg="#39ff14", bg="black")
        self.log_display.pack(fill=tk.X, pady=5)
        
        input_container = tk.Frame(self.main_chat_container)
        input_container.pack(fill=tk.X, pady=5)
        
        # Added Attach File Button
        tk.Button(input_container, text="📎 Attach", width=8, command=self._send_file_workflow).pack(side=tk.LEFT, padx=2)
        
        self.msg_entry = tk.Entry(input_container, font=("Arial", 10))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.msg_entry.bind("<Return>", lambda event: self._send_message_workflow())
        
        tk.Button(input_container, text="Send Message", width=15, command=self._send_message_workflow).pack(side=tk.RIGHT, padx=2)
        
        self.root.after(100, self._process_queue_stream)
        if self.net.is_host:
            self.root.after(500, self._refresh_host_peer_panel)

    def _send_message_workflow(self):
        raw_text = self.msg_entry.get().strip()
        if raw_text:
            # Structuring text data payload into JSON protocol pattern
            packet = {"type": "text", "content": raw_text}
            serialized_packet = json.dumps(packet)
            
            encrypted_payload = logic.encrypt(serialized_packet, self.password)
            self.net.send_message(encrypted_payload)
            
            self.chat_display.insert(tk.END, f"You: {raw_text}\n")
            self.log_display.insert(tk.END, f"[OUTGOING CIPHER]: {encrypted_payload[:40]}...\n")
            self.msg_entry.delete(0, tk.END)

    def _send_file_workflow(self):
        """Opens dialog to choose an image/file, converts to Base64, wraps in JSON, and sends."""
        file_path = filedialog.askopenfilename(title="Select File to Transmit")
        if not file_path:
            return
            
        filename = os.path.basename(file_path)
        
        try:
            # Convert binary file array using logic extension layer
            base64_content = logic.encode_file_to_base64(file_path)
            
            # Pack inside JSON structure mapping types securely
            packet = {
                "type": "file",
                "filename": filename,
                "content": base64_content
            }
            serialized_packet = json.dumps(packet)
            
            encrypted_payload = logic.encrypt(serialized_packet, self.password)
            self.net.send_message(encrypted_payload)
            
            # Reflect action locally in interface consoles
            self.chat_display.insert(tk.END, f"You sent a file: {filename}\n")
            self.log_display.insert(tk.END, f"[OUTGOING FILE CIPHER]: {encrypted_payload[:40]}...\n")
            
            # If the sent file was an image, preview it locally too
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self._render_image_in_chat(file_path, is_self=True)
                
        except Exception as e:
            messagebox.showerror("Transmission Error", f"Failed to encode or transmit file asset: {e}")

    def _render_image_in_chat(self, file_path, is_self=False):
        """Resizes images safely using Pillow and inserts them inline into the ScrolledText widget."""
        try:
            img = Image.open(file_path)
            # Constrain proportions to fit thumbnail mode sizes neatly
            img.thumbnail((150, 150))
            render = ImageTk.PhotoImage(img)
            
            # Keep reference alive
            self.loaded_images.append(render)
            
            label_prefix = "You:\n" if is_self else "Peer:\n"
            self.chat_display.insert(tk.END, label_prefix)
            
            # Inject directly as an embedded window component inside ScrolledText frame
            self.chat_display.image_create(tk.END, image=render)
            self.chat_display.insert(tk.END, "\n\n")
            self.chat_display.see(tk.END)
        except Exception as e:
            print(f"[UI Debug Error] Image preview initialization failed: {e}")

    def _refresh_host_peer_panel(self):
        if self.net.is_host:
            self.peer_listbox.delete(3, tk.END)
            for i, client_socket in enumerate(self.net.clients, start=1):
                try:
                    peer_info = client_socket.getpeername()
                    display_string = f"Peer {i}: {peer_info[0]}:{peer_info[1]}"
                except:
                    display_string = f"Peer {i}: Unknown Endpoint"
                self.peer_listbox.insert(tk.END, display_string)
            self.root.after(1000, self._refresh_host_peer_panel)

    def _process_queue_stream(self):
        while True:
            try:
                raw_payload = self.msg_queue.get_nowait()
                decrypted_json = logic.decrypt(raw_payload, self.password)
                
                # Unpack structured packet mapping
                packet = json.loads(decrypted_json)
                data_type = packet.get("type")
                
                if data_type == "text":
                    text_content = packet.get("content")
                    self.chat_display.insert(tk.END, f"Peer: {text_content}\n")
                    
                elif data_type == "file":
                    filename = packet.get("filename")
                    base64_content = packet.get("content")
                    
                    # Compute safe destination file write handles
                    output_path = os.path.join(self.cache_dir, filename)
                    logic.decode_base64_to_file(base64_content, output_path)
                    
                    self.chat_display.insert(tk.END, f"Peer sent file (Saved to {output_path}): {filename}\n")
                    
                    # If file signature maps to standard image profiles, render directly inline
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        self._render_image_in_chat(output_path, is_self=False)

                self.log_display.insert(tk.END, f"[INCOMING CIPHER]: {raw_payload[:40]}...\n")
                self.chat_display.see(tk.END)
            except queue.Empty:
                break
            except Exception as e:
                # Catch malformed data formats silently or handle failure
                self.log_display.insert(tk.END, f"[Protocol Error Parsing Stream]: {e}\n")
                break
        
        self.root.after(100, self._process_queue_stream)