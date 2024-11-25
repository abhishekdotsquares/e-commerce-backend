from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.requests.request_types import CompanyRequestType
from app.schemas.responses.response_types import CompanyResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

async def createCompany(
    db: AsyncSession,
    business_name: str,
    website_link: str,
    first_name: str,
    last_name: str,
    email: str,
    phone_number: str,
) -> CompanyRequestType:
    """
    Shared logic for creating a company. Can be used by both the createCompany API
    and the approveEnquiryAndCreateCompany API.
    """
    # Validate inputs
    if not business_name or not first_name or not last_name or not email or not phone_number:
        raise ValidationError("All fields are required.")

    # Check if the company ID already exists
    result = await db.execute(select(Company).where(Company.email == email))
    if result.raw.rowcount > 0:
        raise ValidationError(f"company with email {email} already exists.")

    # Create the company
    user = Company(
        business_name=business_name,
        website_link=website_link,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
    )

    # Add and commit
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Return response
    return CompanyResponseType(
        id=user.id,
        business_name=user.business_name,
        website_link=user.website_link,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
    )
