from typing import List
from sqlalchemy import select
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses.types import SubscriptionPlansResponseType
from app.models.subscriptionPlans import SubscriptionPlans
from core.exceptions.validation_error import ValidationError

@strawberry.type
class PlanQuery:
    @strawberry.field
    async def getPlan(self, id: int, info) -> SubscriptionPlansResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the SubscriptionPlans by ID
            plan = await db.get(SubscriptionPlans, id)
            if not plan:
                raise ValidationError(f"Plan with ID {id} not found.")
            
            # Return the company details
            return SubscriptionPlansResponseType(
                id=plan.id,
                name=plan.name,
                description=plan.description,
                price=plan.price,
                duration_days=plan.duration_days,
                currency=plan.currency,
                features=plan.features,
                is_active=plan.is_active,
                trial_days=plan.trial_days,
            )
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise Exception("An unexpected error occurred while fetching the plans.") from e

    @strawberry.field
    async def listPlans(self, info) -> List[SubscriptionPlansResponseType]:
        db: AsyncSession = info.context['db']

        try:
            # Fetch all companies
            result = await db.execute(select(SubscriptionPlans))
            plans = result.scalars().all()

            if not plans:
                raise ValidationError("No plans found.")

            return [
                SubscriptionPlansResponseType(
                    id=plan.id,
                    name=plan.name,
                    description=plan.description,
                    price=plan.price,
                    duration_days=plan.duration_days,
                    currency=plan.currency,
                    features=plan.features,
                    is_active=plan.is_active,
                    trial_days=plan.trial_days,
                )
                for plan in plans
            ]
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise Exception("An unexpected error occurred while listing the plans.") from e
