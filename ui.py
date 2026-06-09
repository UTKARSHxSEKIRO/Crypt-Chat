import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue
import logic
from network import NetworkManager

class CryptChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypt-Chat P2P Portal")
        self.root.geometry("600x500")  # Fixed window geometry syntax
        self.root.minsize(600, 500)
        
        self.msg_queue = queue.Queue()
        self.net = NetworkManager(self.msg_queue)
        self.password = ""

        self._build_welcome_screen()

    def _build_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.root)
        self.welcome_frame.pack(pady=60)

        tk.Label(self.welcome_frame, text="Crypt-Chat P2P Router (Zrok)", font=("Arial", 16, "bold")).pack(pady=15)
        
        tk.Button(self.welcome_frame, text="Host Connection", width=25, command=self._setup_host_workflow).pack(pady=5)
        tk.Button(self.welcome_frame, text="Join Connection", width=25, command=self._setup_guest_workflow).pack(pady=5)

    def _setup_host_workflow(self):
        self.welcome_frame.pack_forget()
        
        # 1-on-1 pure string encryption setup
        self.password = logic.generate_password().strip()
        logic.create_key_file("KEY.json")
        
        self.net.start_as_host(port=5555)
        
        self.host_info_frame = tk.Frame(self.root)
        self.host_info_frame.pack(pady=30)
        
        tk.Label(self.host_info_frame, text="Hosting Active", font=("Arial", 12, "bold"), fg="green").pack(pady=5)
        
        pwd_container = tk.Frame(self.host_info_frame)
        pwd_container.pack(pady=10)
        tk.Label(pwd_container, text=f"Password: {self.password}", font=("Arial", 11, "bold"), bg="#e1e1e1", padx=10, pady=5).pack(side=tk.LEFT)
        tk.Button(pwd_container, text="Copy", command=self._copy_password_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.host_info_frame, text="1. Run your zrok private share tunnel on port 5555").pack()
        tk.Label(self.host_info_frame, text="2. Share your zrok token and password with your peer").pack()
        
        tk.Button(self.host_info_frame, text="Enter Chat Interface", width=25, command=self._build_chat_interface).pack(pady=20)

    def _copy_password_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.password)
        self.root.update()

    def _setup_guest_workflow(self):
        self.welcome_frame.pack_forget()
        
        self.guest_frame = tk.Frame(self.root)
        self.guest_frame.pack(pady=40)
        
        tk.Label(self.guest_frame, text="Enter Connection Parameters", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(self.guest_frame, text="Room Password:").pack()
        self.pwd_entry = tk.Entry(self.guest_frame, width=35)
        self.pwd_entry.pack(pady=2)
        
        tk.Label(self.guest_frame, text="Zrok Local Host (127.0.0.1):").pack()
        self.host_entry = tk.Entry(self.guest_frame, width=35)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(pady=2)
        
        tk.Label(self.guest_frame, text="Zrok Local Access Port:").pack()
        self.port_entry = tk.Entry(self.guest_frame, width=35)
        self.port_entry.pack(pady=2)
        
        tk.Button(self.guest_frame, text="Connect", command=self._connect_guest).pack(pady=15)

    def _connect_guest(self):
        self.password = self.pwd_entry.get().strip()
        host = self.host_entry.get().strip()
        port = int(self.port_entry.get().strip())
        
        try:
            self.net.connect_as_guest(host, port)
            self.guest_frame.pack_forget()
            self._build_chat_interface()
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Refused: {e}")

    def _build_chat_interface(self):
        if hasattr(self, 'host_info_frame'):
            self.host_info_frame.pack_forget()

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main message scroll area
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, height=15, width=65)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Traffic display logger
        tk.Label(self.chat_frame, text="Encrypted Traffic Log:", font=("Arial", 9, "gray")).pack(anchor=tk.W)
        self.log_display = scrolledtext.ScrolledText(self.chat_frame, height=5, width=65, fg="#39ff14", bg="black")
        self.log_display.pack(fill=tk.X, pady=5)
        
        input_container = tk.Frame(self.chat_frame)
        input_container.pack(fill=tk.X, pady=5)
        
        self.msg_entry = tk.Entry(input_container, font=("Arial", 10))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.msg_entry.bind("<Return>", lambda event: self._send_message_workflow())
        
        tk.Button(input_container, text="Send", width=12, command=self._send_message_workflow).pack(side=tk.RIGHT, padx=2)
        
        # Start queue processing check loops
        self.root.after(100, self._process_queue_stream)

    def _send_message_workflow(self):
        raw_text = self.msg_entry.get().strip()
        if raw_text:
            # Directly encrypt the raw text payload string
            encrypted_payload = logic.encrypt(raw_text, self.password)
            self.net.send_message(encrypted_payload)
            
            self.chat_display.insert(tk.END, f"You: {raw_text}\n")
            self.log_display.insert(tk.END, f"[OUTGOING CIPHER]: {encrypted_payload[:40]}...\n")
            self.msg_entry.delete(0, tk.END)
            self.chat_display.see(tk.END)

    def _process_queue_stream(self):
        while True:
            try:
                raw_payload = self.msg_queue.get_nowait()
                # Directly decrypt the incoming network buffer text
                decrypted_text = logic.decrypt(raw_payload, self.password)
                
                self.chat_display.insert(tk.END, f"Peer: {decrypted_text}\n")
                self.log_display.insert(tk.END, f"[INCOMING CIPHER]: {raw_payload[:40]}...\n")
                self.chat_display.see(tk.END)
            except queue.Empty:
                break
        
        self.root.after(100, self._process_queue_stream)