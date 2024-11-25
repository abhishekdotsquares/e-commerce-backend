from sqlalchemy import select
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
import re

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
    ) -> CompanyResponseType:  # Adjust response type to include `status` and `message`
        db: AsyncSession = info.context["db"]
        authorization_header = info.context["authorization"]  # Retrieve authorization header

        # Step 1: Check Authentication
        is_authenticated = await check_authentication(authorization_header)
        if not is_authenticated:
            return CompanyResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )

        try:
            # Step 2: Validate Inputs
            if not business_name or not first_name or not last_name or not email or not phone_number:
                return CompanyResponseType(
                    status=False,
                    message="All fields (business_name, first_name, last_name, email, phone_number) are required."
                )

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return CompanyResponseType(
                    status=False,
                    message="Invalid email format."
                )
                
            # Validate phone number format (assuming a utility function exists)

            # Step 3: Check if a company with the given email already exists
            result = await db.execute(select(Company).where(Company.email == email))
            if result.raw.rowcount > 0:
                return CompanyResponseType(
                    status=False,
                    message=f"A company with email {email} already exists."
                )
            
            # Step 4: Create the Company
            company = Company(
                business_name=business_name,
                website_link=website_link,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )
            print("🐍 File: Mutation/mutation.py | Line: 74 | CompanyMutation: ~ company",company)

            # Add and commit to the database
            db.add(company)
            await db.commit()
            await db.refresh(company)

            # Step 5: Return status Response
            return CompanyResponseType(
                status=True,
                message="Company created successfully.",
                # company_id=company.id  # Include ID in response if available
            )

        except ValidationError as ve:
            # Step 6: Validation Error Handling
            return CompanyResponseType(
                status=False,
                message=str(ve)
            )

        except SQLAlchemyError as sae:
            # Step 7: Handle Database Errors
            await db.rollback()
            return CompanyResponseType(
                status=False,
                message="A database error occurred while creating the company."
            )

        except Exception as e:
            # Step 8: Handle Unexpected Errors
            await db.rollback()
            return CompanyResponseType(
                status=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

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
        authorization_header = info.context['authorization']  # Extract authorization token
        is_authenticated = await check_authentication(authorization_header)

        if is_authenticated:
            try:
                # Fetch the existing company
                company = await db.get(Company, id)
                if not company:
                    return CompanyResponseType(
                        status=False,
                        message=f"Company with ID {id} not found."
                    )

                # Validate at least one field is being updated
                if not any([business_name, website_link, first_name, last_name, email, phone_number]):
                    return CompanyResponseType(
                        status=False,
                        message="At least one field must be provided for update."
                    )

                # Validate email format if it's being updated
                if email is not None and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return CompanyResponseType(
                        status=False,
                        message="Invalid email format."
                    )

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
                    status=True,
                    message="Company details updated successfully."
                )
            except SQLAlchemyError as sae:
                await db.rollback()
                return CompanyResponseType(
                    status=False,
                    message="A database error occurred while updating the company."
                )
            except Exception as e:
                await db.rollback()
                return CompanyResponseType(
                    status=False,
                    message=f"An unexpected error occurred: {e}"
                )
        else:
            return CompanyResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )



    @strawberry.mutation
    async def delete_company(self, id: int, info) -> CompanyResponseType:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization']  # Extract authorization token
        is_authenticated = await check_authentication(authorization_header)

        if is_authenticated:
            try:
                # Fetch the company to be deleted
                company = await db.get(Company, id)
                if not company:
                    return CompanyResponseType(
                        status=False,
                        message=f"Company with ID {id} not found."
                    )

                # Delete the company
                await db.delete(company)
                await db.commit()

                return CompanyResponseType(
                    status=True,
                    message=f"Company with ID {id} has been successfully deleted."
                )
            except SQLAlchemyError as sae:
                await db.rollback()
                return CompanyResponseType(
                    status=False,
                    message="A database error occurred while deleting the company."
                )
            except Exception as e:
                await db.rollback()
                return CompanyResponseType(
                    status=False,
                    message=f"An unexpected error occurred: {e}"
                )
        else:
            return CompanyResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )
