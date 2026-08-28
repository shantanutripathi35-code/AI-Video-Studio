from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd.hash(password)

def verify_password(password: str, password_hash: str):
    return pwd.verify(password, password_hash)

def create_access_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
