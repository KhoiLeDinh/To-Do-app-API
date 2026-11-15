import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext 
import jwt 
from app.core.config import settings
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


    
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