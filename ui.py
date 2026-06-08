import tkinter as tk
from tkinter import filedialog, messagebox
import queue, logic
from network import NetworkManager, HostServer

class CryptChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypt-Chat")
        self.root.geometry("800x450") # Widened the window to fit the sidebar comfortably
        self.msg_queue = queue.Queue()
        self.net = NetworkManager(self.msg_queue)
        self.password = ""
        self.background_server = None
        
        self.show_role_selection()
        self.process_queue()

    def clear_window(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # --- SCREEN 1: Role Selection ---
    def show_role_selection(self):
        self.clear_window()
        tk.Label(self.root, text="Crypt-Chat", font=("Arial", 18)).pack(pady=30)
        tk.Button(self.root, text="Sender (Host)", width=20, command=self.show_sender_screen).pack(pady=10)
        tk.Button(self.root, text="Receiver", width=20, command=self.show_receiver_screen).pack(pady=10)

    # --- SCREEN 2: Sender Path ---
    def show_sender_screen(self):
        self.clear_window()
        self.password = logic.generate_password().strip()
        
        self.background_server = HostServer() 
        self.net.connect('127.0.0.1', 5555) 

        tk.Label(self.root, text="Sender Setup", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Save KEY.json (Browse)", command=self.save_key_file).pack(pady=10)
        
        tk.Label(self.root, text="Key Password (Share securely):").pack()
        pwd_entry = tk.Entry(self.root, width=40)
        pwd_entry.insert(0, self.password)
        pwd_entry.pack(pady=5)
        
        tk.Button(self.root, text="Copy Password", command=lambda: self.root.clipboard_append(self.password)).pack()
        tk.Label(self.root, text="\nWaiting for 2nd user to connect...").pack(pady=10)
        tk.Button(self.root, text="Enter Chat", command=self.show_chat_screen, bg="green", fg="white").pack(pady=20)

    def save_key_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", initialfile="KEY.json")
        if filepath: logic.create_key_file(filepath)

    # --- SCREEN 3: Receiver Path ---
    def show_receiver_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Receiver Setup", font=("Arial", 14)).pack(pady=10)
        
        self.key_path = tk.StringVar()
        tk.Button(self.root, text="Upload KEY.json (Browse)", command=self.load_key_file).pack(pady=5)
        tk.Label(self.root, textvariable=self.key_path).pack()

        tk.Label(self.root, text="Enter Password:").pack(pady=5)
        self.pwd_entry = tk.Entry(self.root, width=40)
        self.pwd_entry.pack()

        tk.Label(self.root, text="Zrok Host (e.g., 127.0.0.1 or api.zrok.io):").pack(pady=5)
        self.host_entry = tk.Entry(self.root, width=30)
        self.host_entry.pack()
        
        tk.Label(self.root, text="Zrok Port (e.g., 5555 or 12345):").pack(pady=5)
        self.port_entry = tk.Entry(self.root, width=15)
        self.port_entry.pack()

        tk.Button(self.root, text="Connect to Chat", command=self.verify_and_connect).pack(pady=20)

    def load_key_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath: self.key_path.set(filepath)

    def verify_and_connect(self):
        if not logic.verify_key_file(self.key_path.get()):
            messagebox.showerror("Error", "Invalid KEY.json file!")
            return
        
        self.password = self.pwd_entry.get().strip()
        host = self.host_entry.get()
        port = self.port_entry.get()
        
        try:
            self.net.connect(host, port)
            self.show_chat_screen()
        except:
            messagebox.showerror("Network Error", "Could not connect to the Sender's network.")

    # --- SCREEN 4: Modern Chat UI with Sidebar ---
    def show_chat_screen(self):
        self.clear_window()
        
        # Left Panel (Main Chat Area)
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(left_frame, text="Decrypted Conversation", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.txt = tk.Text(left_frame, height=18, width=45)
        self.txt.pack(fill=tk.BOTH, expand=True, pady=5)
        
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.ent = tk.Entry(input_frame, width=35)
        self.ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(input_frame, text="Send", command=self.send_msg, width=8).pack(side=tk.LEFT)

        # Right Panel (Encrypted Network Log Sidebar)
        right_frame = tk.Frame(self.root, bg="#e0e0e0", width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 10), pady=10)
        right_frame.pack_propagate(False) # Keep width fixed
        
        tk.Label(right_frame, text="Encrypted Packet Log", font=("Arial", 11, "bold"), bg="#e0e0e0").pack(pady=5, anchor=tk.W, padx=5)
        self.crypto_log = tk.Text(right_frame, height=20, width=30, bg="#2b2b2b", fg="#00ff00", font=("Courier", 9))
        self.crypto_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def send_msg(self):
        msg = self.ent.get()
        if msg:
            encrypted = logic.encrypt(msg, self.password)
            try:
                self.net.send(encrypted)
                
                # Deliver to local display windows
                self.txt.insert(tk.END, f"You: {msg}\n")
                self.crypto_log.insert(tk.END, f"[OUTGOING]: {encrypted[:20]}...\n")
                
                self.ent.delete(0, tk.END)
                self.txt.see(tk.END)
                self.crypto_log.see(tk.END)
            except Exception as e:
                self.txt.insert(tk.END, f"[System ERROR: Disconnected]\n")

    def process_queue(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                decrypted = logic.decrypt(msg, self.password)
                
                # Route incoming packet elements to respective boxes
                self.crypto_log.insert(tk.END, f"[INCOMING]: {msg[:20]}...\n")
                self.txt.insert(tk.END, f"Peer: {decrypted}\n")
                
                self.txt.see(tk.END)
                self.crypto_log.see(tk.END)
        except queue.Empty: pass
        self.root.after(100, self.process_queue)