import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import bcrypt

class CryptoManager:
    def __init__(self):
        # Generate a key for Fernet symmetric encryption
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def generate_key_pair(self):
        """Generate a unique key pair for each user"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(os.urandom(32))
        return key, salt

    def encrypt_message(self, message: str, recipient_key: bytes) -> bytes:
        """Encrypt a message using recipient's public key"""
        try:
            # Convert message to bytes
            message_bytes = message.encode()
            
            # Create a padder
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(message_bytes) + padder.finalize()
            
            # Encrypt using Fernet
            encrypted_data = self.cipher_suite.encrypt(padded_data)
            
            return encrypted_data
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")

    def decrypt_message(self, encrypted_message: bytes, recipient_key: bytes) -> str:
        """Decrypt a message using recipient's private key"""
        try:
            # Decrypt using Fernet
            decrypted_padded = self.cipher_suite.decrypt(encrypted_message)
            
            # Create an unpadder
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            # Convert back to string
            return data.decode()
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

class EncryptedMessage:
    def __init__(self, crypto_manager):
        self.crypto_manager = crypto_manager
    
    def prepare_message(self, sender_id: int, recipient_id: int, 
                       message: str, recipient_key: bytes) -> dict:
        """Prepare a message for sending"""
        encrypted_content = self.crypto_manager.encrypt_message(message, recipient_key)
        
        return {
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': base64.b64encode(encrypted_content).decode(),
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def read_message(self, encrypted_message: dict, recipient_key: bytes) -> str:
        """Read an encrypted message"""
        encrypted_content = base64.b64decode(encrypted_message['content'])
        return self.crypto_manager.decrypt_message(encrypted_content, recipient_key)