from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses.response_types import SubscriptionPlansResponseType
from app.models.subscriptionPlans import SubscriptionPlans
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import stripe
from fastapi import HTTPException

async def createStripePlan(
    db: AsyncSession,
    name: str,
    price: str,
    currency: str,
    duration_days:str
) -> SubscriptionPlansResponseType:
    """
    Shared logic for creating a company. Can be used by both the createCompany API
    and the approveEnquiryAndCreateCompany API.
    """
    # Validate inputs
    if not name or not price or not currency or not duration_days:
        raise ValidationError("All fields are required.")
    
    try:
        # Create the product
        product = stripe.Product.create(name=name)

        # Create the price (plan)
        price = stripe.Price.create(
            unit_amount=price,
            currency=currency,
            recurring={"interval": duration_days, "interval_count": 1},
            product=product.id,
        )

        return price
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error occurred: {e.user_message or str(e)}"
        )


    
