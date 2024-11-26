import strawberry
from typing import List, Optional
from sqlalchemy.future import select
from api.v1.check_auth import check_authentication
from api.v1.response_utils import build_response
from app.models.enquiry import Enquiry
from app.schemas.responses.response_types import CommonResponseType, CompanyResponseType, EnquiriesListResponseType, EnquiryResponseType
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions.validation_error import ValidationError


@strawberry.type
class EnquiryQuery:
    @strawberry.field
    async def getEnquiry(self, id: int, info) -> EnquiryResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']
        is_authenticated = await check_authentication(authorization_header)

        if not is_authenticated:
            return build_response(
                    response_type=CommonResponseType,
                    message="Unauthorized access. Please log in.",
                    status=False,
                )
        try:
            enquiry = await db.get(Enquiry, id)
            if not enquiry:
                return build_response(
                    response_type=CommonResponseType,
                    message=f"Enquiry with ID {id} not found.",
                    status=False,
                )
            return build_response(
                response_type=CommonResponseType,
                status=True,
                message="Enquiry fetched successfully.",
                data={
                    "id": enquiry.id,
                    "business_name": enquiry.business_name,
                    "website_link": enquiry.website_link,
                    "first_name": enquiry.first_name,
                    "last_name": enquiry.last_name,
                    "email": enquiry.email,
                    "phone_number": enquiry.phone_number,
                    "is_approved": enquiry.is_approved,
                },
            )
        except Exception as e:
            return build_response(
                response_type=CommonResponseType,
                message=f"An unexpected error occurred: {e}",
                status=False,
            )

    @strawberry.field
    async def listEnquiries(self, info, limit: int = 10, offset: int = 0) -> EnquiriesListResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']
        is_authenticated = await check_authentication(authorization_header)

        if not is_authenticated:
            return build_response(False, "Unauthorized access. Please log in.")

        try:
            query = select(Enquiry).offset(offset).limit(limit)
            result = await db.execute(query)
            enquiries = result.scalars().all()

            if not enquiries:
                return build_response(False, "No enquiries found.")

            return build_response(
                True,
                "Enquiries fetched successfully.",
                data={
                    "companies": [
                        {
                            "id": enquiry.id,
                            "business_name": enquiry.business_name,
                            "website_link": enquiry.website_link,
                            "first_name": enquiry.first_name,
                            "last_name": enquiry.last_name,
                            "email": enquiry.email,
                            "phone_number": enquiry.phone_number,
                            "is_approved": enquiry.is_approved,
                        }
                        for enquiry in enquiries
                    ],
                },
            )
        except Exception as e:
            return build_response(False, f"An unexpected error occurred: {e}")

    @strawberry.field
    async def filter_enquiries(
        self, info, is_approved: Optional[bool] = None, limit: int = 10, offset: int = 0
    ) -> EnquiriesListResponseType:
        db: AsyncSession = info.context['db']

        try:
            query = select(Enquiry)
            if is_approved is not None:
                query = query.filter(Enquiry.is_approved == is_approved)

            query = query.offset(offset).limit(limit)
            result = await db.execute(query)
            enquiries = result.scalars().all()

            if not enquiries:
                return build_response(False, "No enquiries found.")

            return build_response(
                True,
                "Enquiries fetched successfully.",
                data={
                    "companies": [
                        {
                            "id": enquiry.id,
                            "business_name": enquiry.business_name,
                            "website_link": enquiry.website_link,
                            "first_name": enquiry.first_name,
                            "last_name": enquiry.last_name,
                            "email": enquiry.email,
                            "phone_number": enquiry.phone_number,
                            "is_approved": enquiry.is_approved,
                        }
                        for enquiry in enquiries
                    ],
                },
            )
        except Exception as e:
            return build_response(False, f"Failed to fetch enquiries: {str(e)}")
