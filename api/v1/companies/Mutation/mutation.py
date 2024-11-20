import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses.types import CompanyResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional


@strawberry.type
class CompanyMutation:
    @strawberry.mutation
    async def createCompany(
        self,
        id: int,
        business_name: str,
        website_link: str,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str,
        info
    ) -> CompanyResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not business_name or not first_name or not last_name or not email or not phone_number:
                raise ValidationError("All fields are required.")

            # Check if the company ID already exists
            existing_user = await db.get(Company, id)
            if existing_user:
                raise ValidationError(f"Company with ID {id} already exists.")

            # Create the company
            user = Company(
                id=id,
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
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while creating the company.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while creating the company.") from e

    @strawberry.mutation
    async def updateCompany(
        self,
        id: int,
        info,
        business_name: Optional[str] = None,
        website_link: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> CompanyResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the existing company
            user = await db.get(Company, id)
            if not user:
                raise ValidationError(f"Company with ID {id} not found.")

            # Validate at least one field is being updated
            if not any([business_name, website_link, first_name, last_name, email, phone_number]):
                raise ValidationError("At least one field must be provided for update.")

            # Update fields
            if business_name is not None:
                user.business_name = business_name
            if website_link is not None:
                user.website_link = website_link
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if email is not None:
                user.email = email
            if phone_number is not None:
                user.phone_number = phone_number

            # Commit updates
            await db.commit()
            await db.refresh(user)

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
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while updating the company.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while updating the company.") from e

    @strawberry.mutation
    async def deleteCompany(self, id: int, info) -> str:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the company
            user = await db.get(Company, id)
            if not user:
                raise ValidationError(f"Company with ID {id} not found.")

            # Delete the company
            await db.delete(user)
            await db.commit()

            return f"Company with ID {id} has been successfully deleted."
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while deleting the company.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while deleting the company.") from e
    
