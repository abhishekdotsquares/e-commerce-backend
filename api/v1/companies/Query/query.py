from typing import List
from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.check_auth import check_authentication
from app.schemas.responses.response_types import CompanyResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from core.fastapi.middlewares.authentication import AuthBackend

@strawberry.type
class CompanyQuery:
    @strawberry.field
    async def getCompany(self, id: int, info) -> CompanyResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch the company by ID
                user = await db.get(Company, id)
                if not user:
                    raise ValidationError(f"Company with ID {id} not found.")
                
                # Return the company details
                return CompanyResponseType(
                    id=user.id,
                    business_name=user.business_name,
                    website_link=user.website_link,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone_number=user.phone_number,
                )
            except ValidationError as ve:
                raise ve
            except Exception as e:
                raise Exception("An unexpected error occurred while fetching the company.") from e

    @strawberry.field
    async def listCompanies(self, info) -> List[CompanyResponseType]:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch all companies
                result = await db.execute(select(Company))
                users = result.scalars().all()

                if not users:
                    raise ValidationError("No companies found.")

                return [
                    CompanyResponseType(
                        id=user.id,
                        business_name=user.business_name,
                        website_link=user.website_link,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        phone_number=user.phone_number,
                    )
                    for user in users
                ]
            except ValidationError as ve:
                raise ve
            except Exception as e:
                raise Exception("An unexpected error occurred while listing the companies.") from e
