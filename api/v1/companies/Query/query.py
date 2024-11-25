from typing import List
from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.companyPlanAssociations import CompanyPlanAssociations
from app.schemas.responses.types import CompanyResponseType, SubscriptionPlansResponseType
from app.models.company import Company
from core.exceptions.validation_error import ValidationError
from sqlalchemy.orm import joinedload

@strawberry.type
class CompanyQuery:
    @strawberry.field
    async def getCompany(self, id: int, info) -> CompanyResponseType:
        db: AsyncSession = info.context['db']

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

        try:
            # Fetch all companies
            result = await db.execute(
                select(Company).options(
                    joinedload(Company.subscription_plans).joinedload(CompanyPlanAssociations.plan)
                )
            )

            users = result.unique().scalars().all()


            if not users:
                raise ValidationError("No companies found.")

            company_responses = []

            for user in users:
                # Collect subscription plan details for each company
                plans = [
                    SubscriptionPlansResponseType(
                        id=association.plan.id,
                        name=association.plan.name,
                        price=association.plan.price,
                        duration_days=association.plan.duration_days,
                    )
                    for association in user.subscription_plans if association.plan
                ]


                # Construct the company response
                company_response = CompanyResponseType(
                    id=user.id,
                    business_name=user.business_name,
                    email=user.email,
                    website_link=user.website_link,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    subscription_plans=plans,
                )

                company_responses.append(company_response)

            # Return the response
            return company_responses
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"An unexpected error occurred while listing the companies.{e}") from e
