import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.check_auth import check_authentication
from api.v1.companies.utils.createCompany import createCompany
from app.schemas.requests.request_types import CompanyRequestType
from app.schemas.responses.response_types import CompanyResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional


@strawberry.type
class CompanyMutation:
    @strawberry.mutation
    async def create_company(
        self,
        business_name: str,
        website_link: str,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str,
        info
    ) -> CompanyRequestType:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                return await createCompany(
                    db, business_name, website_link, first_name, last_name, email, phone_number
                )
            except ValidationError as ve:
                raise ve
            except SQLAlchemyError as sae:
                await db.rollback()
                raise Exception("Database error occurred while creating the company.") from sae
            except Exception as e:
                raise Exception("An unexpected error occurred while creating the company.") from e

    @strawberry.mutation
    async def update_company(
        self,
        info,
        id: int,
        business_name: Optional[str] = None,
        website_link: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> CompanyResponseType:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch the existing company
                company = await db.get(Company, id)
                if not company:
                    raise Exception(f"Company with ID {id} not found.")
                
                # Validate at least one field is being updated
                if not any([business_name, website_link, first_name, last_name, email, phone_number]):
                    raise Exception("At least one field must be provided for update.")

                # Update fields
                if business_name is not None:
                    company.business_name = business_name
                if website_link is not None:
                    company.website_link = website_link
                if first_name is not None:
                    company.first_name = first_name
                if last_name is not None:
                    company.last_name = last_name
                if email is not None:
                    company.email = email
                if phone_number is not None:
                    company.phone_number = phone_number

                # Commit updates
                await db.commit()
                await db.refresh(company)

                return CompanyResponseType(
                    id=company.id,
                    business_name=company.business_name,
                    website_link=company.website_link,
                    first_name=company.first_name,
                    last_name=company.last_name,
                    email=company.email,
                    phone_number=company.phone_number,
                )
            except Exception as e:
                await db.rollback()
                raise Exception(f"An error occurred while updating the company: {e}") from e

    @strawberry.mutation
    async def delete_company(self, id: int, info) -> str:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch the company
                company = await db.get(Company, id)
                if not company:
                    raise Exception(f"Company with ID {id} not found.")

                # Delete the company
                await db.delete(company)
                await db.commit()

                return f"Company with ID {id} has been successfully deleted."
            except Exception as e:
                await db.rollback()
                raise Exception(f"An error occurred while deleting the company: {e}") from e