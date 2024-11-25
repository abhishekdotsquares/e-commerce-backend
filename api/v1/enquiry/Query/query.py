import strawberry
from typing import List, Optional
from sqlalchemy.future import select
from api.v1.check_auth import check_authentication
from app.models.enquiry import Enquiry
from app.schemas.responses.response_types import EnquiriesListResponseType, EnquiryResponseType
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions.validation_error import ValidationError


@strawberry.type
class EnquiryQuery:
    @strawberry.field
    async def getEnquiry(self, id: int, info) -> EnquiryResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']  # or another method to get headers
        is_authenticated = await check_authentication(authorization_header)
        
        # If not authenticated, return an error response with status and message
        if not is_authenticated:
            return EnquiryResponseType(
                status=False,
                message="Unauthorized access. Please log in."
            )
        
        try:
            # Fetch the enquiry by ID
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                return EnquiryResponseType(
                    status=False,
                    message=f"Enquiry with ID {id} not found."
                )

            # Return the enquiry details along with the status and message
            return EnquiryResponseType(
                status=True,
                message="Enquiry fetched successfully.",
                id=enquiry.id,
                business_name=enquiry.business_name,
                website_link=enquiry.website_link,
                first_name=enquiry.first_name,
                last_name=enquiry.last_name,
                email=enquiry.email,
                phone_number=enquiry.phone_number,
                is_approved=enquiry.is_approved,
            )
        except Exception as e:
            return EnquiryResponseType(
                status=False,
                message=f"An unexpected error occurred: {e}"
            )

    @strawberry.field
    async def listEnquiries(self, info, limit: int = 10, offset: int = 0) -> EnquiriesListResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']  # Extract authorization token
        is_authenticated = await check_authentication(authorization_header)

        if is_authenticated:
            try:
                # Fetch the enquiries with pagination
                query = select(Enquiry).offset(offset).limit(limit)
                result = await db.execute(query)
                enquiries = result.scalars().all()

                if not enquiries:
                    return EnquiriesListResponseType(
                        status=False,
                        message="No enquiries found.",
                        companies=[]
                    )

                # Return status, message, and enquiries with pagination
                return EnquiriesListResponseType(
                    status=True,
                    message="Enquiries fetched successfully.",
                    companies=[
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
                )
            except Exception as e:
                return EnquiriesListResponseType(
                    status=False,
                    message=f"An unexpected error occurred: {e}",
                    companies=[]
                )
        else:
            return EnquiriesListResponseType(
                status=False,
                message="Unauthorized access. Please log in.",
                companies=[]
            )



    @strawberry.field
    async def filter_enquiries(self, info, is_approved: Optional[bool] = None, limit: int = 10, offset: int = 0) -> EnquiriesListResponseType:
        db: AsyncSession = info.context['db']  # Access the database session from the context
        try:
            # Build the query with optional filter and pagination
            query = select(Enquiry)
            if is_approved is not None:  # Add filter if `is_approved` is provided
                query = query.filter(Enquiry.is_approved == is_approved)

            # Add pagination
            query = query.offset(offset).limit(limit)

            # Execute the query
            result = await db.execute(query)
            enquiries = result.scalars().all()

            if not enquiries:
                return EnquiriesListResponseType(
                    status=False,
                    message="No enquiries found.",
                    companies=[]
                )

            # Return status, message, and enquiries with pagination
            return EnquiriesListResponseType(
                status=True,
                message="Enquiries fetched successfully.",
                companies=[
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
            )
        except Exception as e:
            return EnquiriesListResponseType(
                status=False,
                message=f"Failed to fetch enquiries: {str(e)}",
                companies=[]
            )
