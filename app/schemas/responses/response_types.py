from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
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
    success: bool
    message: str
    
@strawberry.type
class EnquiryResponseType:
    # id: strawberry.ID.
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
class CompanyResponseType:
    # id: strawberry.ID.
    id: int
    business_name: str
    website_link: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    #subscription_plans: list[SubscriptionPlansResponseType]
    
@strawberry.type
class CompanySubscribedPlansResponse:
    id: int
    company_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool