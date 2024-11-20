import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.companies.utils.createCompany import createCompany
from app.models.enquiry import Enquiry
from app.schemas.requests.request_types import EnquiryRequestType
from app.schemas.responses.response_types import CompanyResponseType, EnquiryResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional


@strawberry.type
class EnquiryMutation:
    @strawberry.mutation
    async def createEnquiry(
        self,
        business_name: str, 
        website_link: str,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str,
        is_approved: bool,
        info
    ) -> EnquiryRequestType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not business_name or not first_name or not last_name or not email or not phone_number or not is_approved:
                raise ValidationError("All fields are required.")

            # Check if the Enquiry ID already exists
            existing_user = await db.get(Enquiry, id)
            if existing_user:
                raise ValidationError(f"Enquiry with ID {id} already exists.")
            

            # Create the company
            user = Enquiry(
                business_name=business_name,
                website_link=website_link,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                is_approved=False
            )

            # Add and commit
            db.add(user)
            await db.commit()
            await db.refresh(user)

            # Return response
            return EnquiryResponseType(
                id=user.id,
                business_name=user.business_name,
                website_link=user.website_link,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone_number=user.phone_number,
                is_approved=user.is_approved,
            )
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while submitting the enquiry.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while submitting the enquiry.") from e
    
    @strawberry.mutation
    async def approveEnquiry(self, id: int, info) -> str:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the Enquiry by ID
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                raise ValidationError(f"No enquiry found with ID {id}.")

            # Check if it's already approved
            if enquiry.is_approved:
                raise ValidationError(f"Enquiry with ID {id} is already approved.")

            # Update the status to approved
            enquiry.is_approved = True
            await db.commit()
            await db.refresh(enquiry)

            # Call the createCompany API
            try:
                company_payload = {
                    "db": db,
                    "business_name": enquiry.business_name,
                    "website_link": enquiry.website_link,
                    "first_name": enquiry.first_name,
                    "last_name": enquiry.last_name,
                    "email": enquiry.email,
                    "phone_number": enquiry.phone_number,
                }
                # Assuming createCompany is another Strawberry mutation or service function
                company_response = await createCompany(**company_payload)
                if company_response.id:  # Check if the company id exists to confirm success
                    return f"Enquiry with ID {id} approved and company created successfully."
                else:
                    raise Exception("Error while creating the company. Approval reverted.")

            except Exception as e:
                # Rollback the approval if company creation fails
                enquiry.is_approved = False
                await db.commit()
                raise Exception("Error while creating the company. Approval reverted.") from e

        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while approving the enquiry.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while processing the approval and company creation.") from e
