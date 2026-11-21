import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext 
import jwt 
from app.core.config import settings
from datetime import datetime, timedelta, timezone
import bcrypt

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY
ENCRYPTION_KEY = settings.ENCRYPTION_KEY

def hash_password(password: str) -> str:
    # Mã hóa password trực tiếp bằng bcrypt, tự động cắt ngắn dưới 72 bytes
    pwd_bytes = password.encode('utf-8')
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # So khớp password trực tiếp bằng bcrypt
    pwd_bytes = plain_password.encode('utf-8')
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
    except ValueError:
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#Generate Fernet key for encryption and recryption
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

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