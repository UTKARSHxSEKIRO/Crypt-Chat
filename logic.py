import base64, hashlib, json, random, string
from cryptography.fernet import Fernet

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=25))

def create_key_file(filepath):
    with open(filepath, 'w') as f:
        json.dump({"auth": "crypt-chat-valid-key"}, f)

def verify_key_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f).get("auth") == "crypt-chat-valid-key"
    except:
        return False

def get_cipher(password):
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    return Fernet(key)

def encrypt(msg, pwd): 
    return get_cipher(pwd).encrypt(msg.encode()).decode()

def decrypt(msg, pwd):
    try: return get_cipher(pwd).decrypt(msg.encode()).decode()
    except: return "[Decryption Failed]"
import base64

def encode_file_to_base64(file_path):
    """Converts any binary file or image into a secure Base64 text string."""
    with open(file_path, "rb") as file:
        binary_data = file.read()
        base64_bytes = base64.b64encode(binary_data)
        return base64_bytes.decode('utf-8')

def decode_base64_to_file(base64_string, output_path):
    """Reverts a Base64 text string back into its original binary file format."""
    binary_data = base64.b64decode(base64_string.encode('utf-8'))
    with open(output_path, "wb") as file:
        file.write(binary_data)