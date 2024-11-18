from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class CompanyResponse(BaseModel):
    business_name: str
    website_link: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None

    class Config:
        """Configuration for the Pydantic model."""
        
        from_attributes = True  # Allows the model to populate from attributes
