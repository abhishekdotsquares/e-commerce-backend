from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime
import graphene
import strawberry

    
@strawberry.type
class EnquiryRequestType:
    # id: strawberry.ID.
    business_name: str
    website_link: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    status:bool
    message:str
    
@strawberry.type
class CompanyRequestType:
    # id: strawberry.ID.
    business_name: str
    website_link: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    
@strawberry.type
class UserRequestType:
    # id: strawberry.ID.
    email: str
    password: str
    is_superuser: bool
