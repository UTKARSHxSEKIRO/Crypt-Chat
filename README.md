# Crypt Chat
 A secure chating app that works on local network and Zgrok
```markdown
# Crypt-Chat 🔐

A simple, secure, and fully encrypted desktop chat application built in Python. It allows two people to text each other long-distance over the internet without needing a central server or exposing their home network setup.

## How it Works
* **Real Encryption:** Messages are scrambled using AES-256 encryption on your computer *before* they ever touch the network. If someone intercepts your data, all they will see is random gibberish.
* **Dual-Display View:** The app features a split-screen dashboard. The left side shows your clean, decrypted conversation, while the right sidebar shows the live, encrypted network data flashing in real-time.
* **No Server Needed:** Using a free tool called **zrok**, the app creates a temporary, private "portal" through the internet to safely connect you and your friend's machines directly.

---

## Setup & Installation

Both you and your friend need to complete these quick installation steps:

1. **Clone the project and open the folder:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Crypt-Chat.git](https://github.com/YOUR_USERNAME/Crypt-Chat.git)
   cd Crypt-Chat

```

2. **Set up a Python Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate

```


3. **Install the encryption package:**
```bash
pip install cryptography

```


4. **Install zrok:**
Make sure you have `zrok` installed on your system and connected to a free account at [zrok.io](https://zrok.io). Run `zrok enable <your-token>` in your terminal to activate it.

---

## How to Chat (Long-Distance Step-by-Step)

### Person A (The Sender / Host)

1. Run the app entry point in your terminal:
```bash
python main.py

```


2. Click **Sender (Host)**.
3. Click **Save KEY.json** to save your security key file somewhere safe on your computer.
4. Click **Copy Password** to copy your automatically generated 25-character secret key.
5. Click **Enter Chat**. Your app window is now waiting for your friend to connect.
6. Open a *second, separate terminal tab* and turn on the public portal by running:
```bash
zrok share private 127.0.0.1:5555 --backend-mode tcpTunnel

```


7. Look at the terminal output. Copy the long **private share token** string that it gives you.
8. Send three things to your friend (via WhatsApp or Discord): Your `KEY.json` file, the 25-character password, and the zrok share token.

### Person B (The Receiver / Client)

1. Open your terminal and turn on your side of the zrok portal using the token your friend sent you:
```bash
zrok access private <PASTE_SENDER_SHARE_TOKEN_HERE>

```


2. Look closely at your terminal output. It will say something like: `Allocated local endpoint: 127.0.0.1:9191`. Take note of that port number (`9191`).
3. Open a *second terminal window* and start the app:
```bash
python main.py

```


4. Click **Receiver**.
5. Upload the `KEY.json` file you downloaded from your friend, paste the 25-character password, and type in the port number (`9191`) given by your zrok terminal.
6. Click **Connect to Chat** and start texting!

```

```
