from datetime import datetime, timedelta
from http.client import HTTPException
from typing import Optional
# from core.config import config
import jwt 
import os
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.models.user import User 


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    """
    to_encode = data.copy()

    # Set token expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES")))
    
    # Include expiration time
    to_encode.update({"exp": expire})

    # Optionally add user id or email for identification
    if "sub" not in to_encode:
        raise ValueError("Subject (sub) must be included in token payload")

    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt


def validate_jwt_token(token: str):
    try:
        # Decode the token
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])

        # Extract the email (subject) from payload
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=403, detail="Invalid token: Missing subject (sub)")

        # You can return payload or user_id here if needed
        return payload  # Return full payload or other user-specific data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.JWTError as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")


async def decode_access_token(token: str, db: AsyncSession) -> dict:
    """
    Decodes a JWT token, verifies its validity, and checks if the user exists.
    """
    try:
        # Decode the token to get the payload
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        
        # Extract the user identifier (could be user_id, email, etc.)
        user_id = payload.get("sub")  # Assuming the user identifier is in 'sub'
        if user_id is None:
            raise HTTPException(status_code=403, detail="Token does not contain user information")

        # Check if the user exists in the database
        async with db.begin():
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=403, detail="User not found or token is invalid")

        # Optionally, you can also check for other conditions like user's account status, etc.
        
        return user  # Return the user or any other relevant data you need

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

