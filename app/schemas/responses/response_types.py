from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import graphene
# from graphene import Field, ObjectType, Mutation, String, UUID
import strawberry

@strawberry.type
class TokenType:
    access_token: str
    token_type: str
    refresh_token: str

@strawberry.type
class ForgotPasswordResponseType:
    status: bool
    message: str
    
@strawberry.type
class EnquiryResponseType:
    status: bool
    message: str
    id: Optional[int] = None
    business_name: Optional[str] = None
    website_link: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_approved: Optional[bool] = None
    
@strawberry.type
class CompanyResponseType:
    status: bool
    message: str
    id: Optional[int] = None
    business_name: Optional[str] = None
    website_link: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
   
@strawberry.type
class CompaniesListResponseType:
    status: bool
    message: str
    companies: List[CompanyResponseType]
    total_pages: Optional[int] = None
    total_records: Optional[int] = None
    
@strawberry.type
class EnquiriesListResponseType:
    status: bool
    message: str
    enquiries: List[CompanyResponseType]
  
@strawberry.type
class UserResponseType:
    status: bool
    message: str
    id: Optional[int] = None
    email: Optional[str] = None
    is_superuser: Optional[bool] = None

@strawberry.type
class LoginResponseType:
    status: bool
    message: str
    access_token: Optional[str] = None  # Make access_token nullable
    refresh_token: Optional[str] = None  # Make refresh_token nullable

