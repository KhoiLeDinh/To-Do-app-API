import os
from cryptography.fernet import Fernet

#Generate Fernet key for encryption and recryption
SECRET_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(SECRET_KEY)

#Create encryption and decryption functions
#Encryption Function
def encrypt_text(plain_text: str) -> str:
    if not plain_text:
        return ""
    return cipher_suite.encrypt(plain_text.encode("utf-8")).decode("utf-8")

#Decryption Function
def decrypt_text(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    try: 
        return cipher_suite.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""