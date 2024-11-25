import strawberry
from typing import List, Optional
from sqlalchemy.future import select
from api.v1.check_auth import check_authentication
from app.models.enquiry import Enquiry
from app.schemas.responses.response_types import EnquiryResponseType
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions.validation_error import ValidationError


@strawberry.type
class EnquiryQuery:
    @strawberry.field
    async def getEnquiry(self, id: int, info) -> EnquiryResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch the company by ID
                user = await db.get(Enquiry, id)
                if not user:
                    raise ValidationError(f"Enquiry with ID {id} not found.")
                
                # Return the company details
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
            except Exception as e:
                raise Exception("An unexpected error occurred while fetching the enquiry.") from e

    @strawberry.field
    async def listEnquiries(self, info) -> List[EnquiryResponseType]:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Fetch all companies
                result = await db.execute(select(Enquiry))
                users = result.scalars().all()

                if not users:
                    raise ValidationError("No enquiries found.")

                return [
                    EnquiryResponseType(
                        id=user.id,
                        business_name=user.business_name,
                        website_link=user.website_link,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        phone_number=user.phone_number,
                        is_approved=user.is_approved,
                    )
                    for user in users
                ]
            except ValidationError as ve:
                raise ve
            except Exception as e:
                raise Exception("An unexpected error occurred while listing the enquiries.") from e


    @strawberry.field
    async def filter_enquiries(self, info, is_approved: Optional[bool] = None) -> List[EnquiryResponseType]:
        db = info.context['db']  # Access the database session from the context
        try:
            # Build the query
            query = select(Enquiry)
            if is_approved is not None:  # Add filter if `is_approved` is provided
                query = query.filter(Enquiry.is_approved == is_approved)

            # Execute the query
            result = await db.execute(query)
            enquiries = result.scalars().all()

            # Map to the GraphQL type
            return [
                EnquiryResponseType(
                    id=enquiry.id,
                    business_name=enquiry.business_name,
                    website_link=enquiry.website_link,
                    first_name=enquiry.first_name,
                    last_name=enquiry.last_name,
                    email=enquiry.email,
                    phone_number=enquiry.phone_number,
                    is_approved=enquiry.is_approved,
                )
                for enquiry in enquiries
            ]
        except Exception as e:
            raise Exception(f"Failed to fetch enquiries: {str(e)}")