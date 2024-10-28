import uuid
import hashlib
from datetime import datetime, timedelta
from fastapi import HTTPException

class TokenHandler:
    @staticmethod
    def generate_reset_token(email: str) -> str:
        # Generate a unique UUID
        unique_id = str(uuid.uuid4())
        
        # Hash the email
        hashed_email = hashlib.sha256(email.encode()).hexdigest()
        
        # Get the current time in UTC and add 1 minute for expiration
        expiration_time = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
        
        # Combine the UUID, hashed email, and expiration time to create the token
        token = f"{unique_id}:{hashed_email}:{expiration_time}"
        
        return token

    @staticmethod
    def validate_reset_token(token: str, email: str) -> bool:
        # Split the token into UUID, hashed email, and expiration time
        try:
            unique_id, hashed_email, expiration_time_str = token.split(":")
            expiration_time = float(expiration_time_str)
        except ValueError:
            return False
        
        # Check if the token is expired
        if datetime.utcnow().timestamp() > expiration_time:
            return False
        
        # Hash the provided email and compare
        expected_hashed_email = hashlib.sha256(email.encode()).hexdigest()
        
        return hashed_email == expected_hashed_email
