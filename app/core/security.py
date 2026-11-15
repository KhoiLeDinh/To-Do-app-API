import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext 

#Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Password hashing function
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#Password verification function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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