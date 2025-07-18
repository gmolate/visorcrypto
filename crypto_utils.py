import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def buffer_to_hex(buffer: bytes) -> str:
    """Converts bytes to a hex string."""
    return buffer.hex()

def hex_to_buffer(hex_string: str) -> bytes:
    """Converts a hex string to bytes."""
    return bytes.fromhex(hex_string)

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a key using PBKDF2HMAC with SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 key length
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_api_keys(api_keys: dict, password: str) -> dict:
    """Encrypts API keys using AES-GCM."""
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    api_keys_json = json.dumps(api_keys).encode('utf-8')

    encrypted_data = aesgcm.encrypt(iv, api_keys_json, None)

    return {
        'encryptedHex': buffer_to_hex(encrypted_data),
        'ivHex': buffer_to_hex(iv),
        'saltHex': buffer_to_hex(salt),
    }

def decrypt_api_keys(encrypted_hex: str, iv_hex: str, salt_hex: str, password: str) -> dict:
    """Decrypts API keys using AES-GCM."""
    salt = hex_to_buffer(salt_hex)
    iv = hex_to_buffer(iv_hex)
    key = derive_key(password, salt)

    encrypted_data = hex_to_buffer(encrypted_hex)

    aesgcm = AESGCM(key)
    decrypted_data = aesgcm.decrypt(iv, encrypted_data, None)

    decrypted_json = decrypted_data.decode('utf-8')
    return json.loads(decrypted_json)
