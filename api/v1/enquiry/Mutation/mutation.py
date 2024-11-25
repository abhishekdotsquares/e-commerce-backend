from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.check_auth import check_authentication
from api.v1.companies.utils.createCompany import createCompany
from app.models.enquiry import Enquiry
from app.schemas.requests.request_types import EnquiryRequestType
from app.schemas.responses.response_types import CompanyResponseType, EnquiryResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import re

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
        info
    ) -> EnquiryResponseType:
        db: AsyncSession = info.context["db"]
        try:
            # Step 1: Validate inputs
            if not business_name or not first_name or not last_name or not email or not phone_number:
                return EnquiryResponseType(
                    status=False,
                    message="All fields are required."
                )

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return EnquiryResponseType(
                    status=False,
                    message="Invalid email format."
                )

            # Step 2: Check if the enquiry with the same email already exists
            result = await db.execute(select(Enquiry).where(Enquiry.email == email))
            if result.raw.rowcount > 0:
                return EnquiryResponseType(
                    status=False,
                    message=f"An enquiry with email {email} already exists."
                )

            # Step 3: Create the enquiry object
            enquiry = Enquiry(
                business_name=business_name,
                website_link=website_link,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                is_approved=False
            )

            # Step 4: Add and commit the new enquiry
            db.add(enquiry)
            await db.commit()
            await db.refresh(enquiry)

            # Step 5: Return status response
            return EnquiryResponseType(               
                status=True,
                message="Enquiry created successfully. Please wait for approval."
            )

        except SQLAlchemyError as sae:
            # Rollback in case of DB error
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message="Database error occurred while submitting the enquiry."
            )
        
        except Exception as e:
            return EnquiryResponseType(
                status=False,
                message="An unexpected error occurred while submitting the enquiry."
            )
    
    @strawberry.mutation
    async def update_enquiry(
        self,
        info,
        id: int,
        business_name: Optional[str] = None,
        website_link: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_approved: Optional[bool] = None,
    ) -> EnquiryResponseType:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization']  # Replace with your authentication method

        # Step 1: Check authentication
        is_authenticated = await check_authentication(authorization_header)
        if not is_authenticated:
            return EnquiryResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )

        try:
            # Step 2: Fetch the enquiry record by ID
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                return EnquiryResponseType(
                    status=False,
                    message=f"Enquiry with ID {id} not found."
                )

            # Step 3: Validate that at least one field is provided for update
            if not any([business_name, website_link, first_name, last_name, email, phone_number, is_approved]):
                return EnquiryResponseType(
                    status=False,
                    message="At least one field must be provided for update."
                )

            # Step 4: Validate specific fields
            if email is not None:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return EnquiryResponseType(
                        status=False,
                        message="Invalid email format."
                    )

            if phone_number is not None:
                if not re.match(r"^\d{10}$", phone_number):
                    return EnquiryResponseType(
                        status=False,
                        message="Invalid phone number format. It should contain 10 digits."
                    )

            # Step 5: Update the enquiry fields
            if business_name is not None:
                enquiry.business_name = business_name
            if website_link is not None:
                enquiry.website_link = website_link
            if first_name is not None:
                enquiry.first_name = first_name
            if last_name is not None:
                enquiry.last_name = last_name
            if email is not None:
                enquiry.email = email
            if phone_number is not None:
                enquiry.phone_number = phone_number
            if is_approved is not None:
                enquiry.is_approved = is_approved

            # Step 6: Commit updates
            await db.commit()
            await db.refresh(enquiry)

            # Step 7: Return status response
            return EnquiryResponseType(
                status=True,
                message="Enquiry updated successfully."
            )

        except SQLAlchemyError as sae:
            # Rollback changes in case of a database error
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message="Database error occurred while updating the enquiry."
            )

        except Exception as e:
            # Rollback changes in case of unexpected errors
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message=f"An unexpected error occurred: {str(e)}"
            )
    @strawberry.mutation
    async def delete_enquiry(
        self, 
        id: int, 
        info
    ) -> EnquiryResponseType:
        db: AsyncSession = info.context["db"]  # Access database session
        authorization_header = info.context["authorization"]  # Access authorization header

        # Step 1: Check authentication
        is_authenticated = await check_authentication(authorization_header)
        if not is_authenticated:
            return EnquiryResponseType(
                status=False,
                message="Unauthorized request. Please provide valid credentials."
            )

        try:
            # Step 2: Fetch the enquiry by ID
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                return EnquiryResponseType(
                    status=False,
                    message=f"Enquiry with ID {id} not found."
                )

            # Step 3: Delete the enquiry
            await db.delete(enquiry)
            await db.commit()

            # Step 4: Return status response
            return EnquiryResponseType(
                status=True,
                message=f"Enquiry with ID {id} has been successfully deleted."
            )

        except SQLAlchemyError as sae:
            # Rollback changes in case of database errors
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message="Database error occurred while deleting the enquiry."
            )

        except Exception as e:
            # Rollback changes for any unexpected errors
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message=f"An unexpected error occurred: {str(e)}"
            )
    
    @strawberry.mutation
    async def approveEnquiry(self, id: int, info) -> EnquiryResponseType:
        db: AsyncSession = info.context["db"]
        authorization_header = info.context["authorization"]  # Retrieve authorization header

        # Step 1: Check authentication
        is_authenticated = await check_authentication(authorization_header)
        if not is_authenticated:
            return EnquiryResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )

        try:
            # Step 2: Fetch the Enquiry by ID
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                return EnquiryResponseType(
                    status=False,
                    message=f"No enquiry found with ID {id}."
                )

            # Step 3: Check if it's already approved
            if enquiry.is_approved:
                return EnquiryResponseType(
                    status=False,
                    message=f"Enquiry with ID {id} is already approved."
                )

            # Step 4: Approve the enquiry
            enquiry.is_approved = True
            await db.commit()  # Save approval in the database
            await db.refresh(enquiry)

            # Step 5: Create a company for the approved enquiry
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
                # Assuming `createCompany` is a callable function
                company_response = await createCompany(**company_payload)

                # Check if the company was successfully created
                if getattr(company_response, "id", None):  # Ensure company creation returned an ID
                    return EnquiryResponseType(
                        status=True,
                        message=f"Enquiry with ID {id} approved and company created successfully."
                    )
                else:
                    raise Exception("Error while creating the company. Approval reverted.")

            except Exception as e:
                # Rollback the approval if company creation fails
                enquiry.is_approved = False
                await db.commit()
                return EnquiryResponseType(
                    status=False,
                    message=f"An error occurred while creating the company: {str(e)}. Approval reverted."
                )

        except ValidationError as ve:
            return EnquiryResponseType(
                status=False,
                message=str(ve)
            )

        except SQLAlchemyError as sae:
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message="Database error occurred while approving the enquiry."
            )

        except Exception as e:
            await db.rollback()
            return EnquiryResponseType(
                status=False,
                message=f"An unexpected error occurred: {str(e)}"
            )

