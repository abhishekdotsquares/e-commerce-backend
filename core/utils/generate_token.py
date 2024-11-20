from datetime import datetime, timedelta
from typing import Optional
# from core.config import config
import jwt 
import os 


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=os.getenv("JWT_EXPIRE_MINUTES"))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt