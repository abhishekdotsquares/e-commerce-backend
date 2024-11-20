# app/schemas/requests/companies.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
import strawberry
import graphene
# from graphene import Field, ObjectType, Mutation, String, UUID

# from app.schemas.responses.companies import UUIDScalar

# class CompanyCreate(BaseModel):
#     business_name: str = Field(..., title="Business Name", max_length=255)
#     website_link: str = Field(..., title="Website URL", max_length=255)
#     first_name: str = Field(..., title="First Name", max_length=50)
#     last_name: str = Field(..., title="Last Name", max_length=50)
#     email: EmailStr = Field(..., title="Email Address")
#     phone_number: str = Field(..., title="Phone Number", max_length=20)

#     class Config:
#         from_attributes = True  # Allows the model to populate from attributes


# Input type for creating a Company
@strawberry.input
class CompanyCreate:
    id: strawberry.ID
    business_name: str
    website_link: str
    first_name: str
    last_name: str
    email: str
    phone: str
# Input type for updating a Company
@strawberry.input
class CompanyUpdate:
    id: strawberry.ID
    business_name: str
    website_link: str
    first_name: str
    last_name: str
    email: str
    phone: str

