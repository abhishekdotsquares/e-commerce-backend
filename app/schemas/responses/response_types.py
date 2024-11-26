from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import graphene
# from graphene import Field, ObjectType, Mutation, String, UUID
import strawberry
from strawberry.scalars import JSON  # Import the JSON scalar

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
class UserResponseType:
    # id: strawberry.ID.
    id: int
    email: str
    password: str
    is_superuser: bool

@strawberry.type
class SubscriptionPlansResponseType:
    id: int
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int
    currency: Optional[str] = "USD"
    features: Optional[str] = None
    is_active: bool = True
    trial_days: int = 0

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
    data: Optional[JSON] = None
   
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
    data: Optional[JSON] = None

    access_token: Optional[str] = None  # Make access_token nullable
    refresh_token: Optional[str] = None  # Make refresh_token nullable
    
@strawberry.type
class CommonResponseType:
    status: bool
    message: str
    data: Optional[JSON] = None
    
@strawberry.type
class CompanySubscribedPlansResponse:
    id: int
    company_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool