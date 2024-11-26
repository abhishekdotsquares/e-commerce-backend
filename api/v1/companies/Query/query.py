from typing import List
from sqlalchemy import func, select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.check_auth import check_authentication
from api.v1.response_utils import build_response
from app.schemas.responses.response_types import CompaniesListResponseType, CompanyResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from core.fastapi.middlewares.authentication import AuthBackend

@strawberry.type
class CompanyQuery:
    @strawberry.field
    async def getCompany(self, id: int, info) -> CompanyResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']  # Extract authorization token
        is_authenticated = await check_authentication(authorization_header)        
        if is_authenticated:
            try:
                # Fetch the company by ID
                company = await db.get(Company, id)
                if not company:
                    return build_response(
                        response_type=CompanyResponseType,
                        message=f"Company with ID {id} not found.",
                        status=False
                    )

                # Return the company details
                return build_response(
                    response_type=CompanyResponseType,
                    message="Company details fetched successfully.",
                    status=True,
                    data={
                        'id': company.id,
                        'business_name': company.business_name,
                        'website_link': company.website_link,
                        'first_name': company.first_name,
                        'last_name': company.last_name,
                        'email': company.email,
                        'phone_number': company.phone_number,
                    }
                )
            except Exception as e:
                return build_response(
                    response_type=CompanyResponseType,
                    message=f"An unexpected error occurred: {e}",
                    status=False
                )
        else:
            return build_response(
                response_type=CompanyResponseType,
                message="Unauthorized access. Please log in.",
                status=False
            )

    @strawberry.field
    async def listCompanies(self, info, page: int = 1, page_size: int = 10) -> CompaniesListResponseType:
        db: AsyncSession = info.context['db']
        authorization_header = info.context['authorization']  # Extract authorization token
        is_authenticated = await check_authentication(authorization_header)

        if is_authenticated:
            try:
                # Validate pagination inputs
                if page < 1 or page_size < 1:
                    return build_response(
                        response_type=CompaniesListResponseType,
                        message="Page and page_size must be greater than 0.",
                        status=False,
                        data={'companies': []}
                    )

                # Calculate offset and limit for pagination
                offset = (page - 1) * page_size
                query = select(Company).offset(offset).limit(page_size)

                # Fetch paginated companies
                result = await db.execute(query)
                companies = result.scalars().all()

                # Count total records for total_pages calculation
                total_records_query = await db.execute(select(func.count(Company.id)))
                total_records = total_records_query.scalar() or 0
                total_pages = (total_records + page_size - 1) // page_size  # Calculate total pages

                if not companies:
                    return build_response(
                        response_type=CompaniesListResponseType,
                        message="No companies found.",
                        status=False,
                        data={
                            'companies': [],
                            'total_pages': total_pages,
                            'total_records': total_records
                        }
                    )

                # Return status, message, companies, and pagination metadata
                return build_response(
                    response_type=CompaniesListResponseType,
                    message="Companies fetched successfully.",
                    status=True,
                    data={
                        'companies': [
                            CompanyResponseType(
                                status=True,
                                message="",
                                id=company.id,
                                business_name=company.business_name,
                                website_link=company.website_link,
                                first_name=company.first_name,
                                last_name=company.last_name,
                                email=company.email,
                                phone_number=company.phone_number,
                            )
                            for company in companies
                        ],
                        'total_pages': total_pages,
                        'total_records': total_records
                    }
                )
            except Exception as e:
                return build_response(
                    response_type=CompaniesListResponseType,
                    message=f"An unexpected error occurred: {e}",
                    status=False,
                    data={'companies': [], 'total_pages': 0, 'total_records': 0}
                )
        else:
            return build_response(
                response_type=CompaniesListResponseType,
                message="Unauthorized access. Please log in.",
                status=False,
                data={'companies': [], 'total_pages': 0, 'total_records': 0}
            )
