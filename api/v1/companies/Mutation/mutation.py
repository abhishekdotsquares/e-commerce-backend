from datetime import datetime, timedelta
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.check_auth import check_authentication
from api.v1.companies.utils.createCompany import createCompany
from app.schemas.requests.request_types import CompanyRequestType
from app.schemas.responses.response_types import CompanyResponseType,CompanySubscribedPlansResponse
from app.models.company import Company
from app.models.subscriptionPlans import SubscriptionPlans
from app.models.companyPlanAssociations import CompanyPlanAssociations
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from core.utils.email import send_email


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

    @strawberry.mutation
    async def createCompanySubscribedPlan(
        self,
        company_id: int,
        plan_id: int,
        is_active: bool,
        info
    ) -> CompanySubscribedPlansResponse:
        """
        Creates a company subscription plan and sends an email notification.

        Args:
            company_id (int): ID of the company subscribing to the plan.
            plan_id (int): ID of the subscription plan.
            is_active (bool): Whether the subscription is active.
            info: GraphQL context containing the database session.

        Returns:
            CompanySubscribedPlansResponse: Response containing subscription details.
        """
        db: AsyncSession = info.context["db"]
        authorization_header = info.context['authorization'] # or another method to get headers
        is_authenticated=await check_authentication(authorization_header)
        if is_authenticated:
            try:
                # Calculate start and end dates
                start_date = datetime.now()
                end_date = start_date + timedelta(days=15)

                # Create the subscription plan record
                new_plan = CompanyPlanAssociations(
                    company_id=company_id,
                    plan_id=plan_id,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=is_active,
                )

                # Add and commit the new plan to the database
                db.add(new_plan)
                await db.commit()
                await db.refresh(new_plan)

                # Fetch plan details
                plan_details = await db.get(SubscriptionPlans, plan_id)
                # Fetch company details
                company_details = await db.get(Company, company_id)
                if company_details and company_details.email:
                    # Compose and send the email
                    email_body = f"""
                    <p>Dear {company_details.business_name or company_details.email},</p>
                    
                    <p>We are pleased to confirm your subscription to our {plan_details.name} plan. Your subscription will be effective immediately, and you are entitled to a 15-day trial period, starting from {start_date}, to explore the full benefits of the plan.</p>

                    <p>Should you have any questions or require assistance during your trial period, please do not hesitate to contact our support team at support.harmannn@harman.com or visit our support portal.</p>

                    <p>We look forward to serving your business and supporting your continued growth.</p>

                    <p>Best regards,<br>
                    The Harmann Studios Team</p>
                    """
                    await send_email(
                        to_email=company_details.email,
                        subject="Subscription Plan Confirmation",
                        body=email_body,
                    )

                # Return the response object
                return CompanySubscribedPlansResponse(
                    id=new_plan.id,
                    company_id=new_plan.company_id,
                    plan_id=new_plan.plan_id,
                    start_date=new_plan.start_date,
                    end_date=new_plan.end_date,
                    is_active=new_plan.is_active,
                )
            except Exception as e:
                # Rollback in case of any errors
                await db.rollback()
                raise Exception(f"Error creating subscription plan: {str(e)}")
