import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses.types import SubscriptionPlansResponseType
from app.models.subscriptionPlans import SubscriptionPlans
from core.exceptions.validation_error import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from sqlalchemy.future import select

@strawberry.type
class PlanMutation:
    @strawberry.mutation
    async def createPlan(
        self,
        id: int,
        name: str,
        description: str,
        price: float,
        durationDays: int,
        currency: str,
        features: str,
        isActive: bool,
        trialDays: int,
        info
    ) -> SubscriptionPlansResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not name or not price or not durationDays :
                raise ValidationError("All fields are required.")

            # Check if the plan ID already exists
            existing_plan = await db.get(SubscriptionPlans, id)
            if existing_plan:
                raise ValidationError(f"Plan with ID {id} already exists.")

            # Create the plan
            plan = SubscriptionPlans(
                id=id,
                name=name,
                description=description,
                price=price,
                duration_days=durationDays,
                currency=currency,
                features=features,
                is_active=isActive,
                trial_days=trialDays,
            )

            # Add and commit
            db.add(plan)
            await db.commit()
            await db.refresh(plan)

            # Return response
            return SubscriptionPlansResponseType(
                id=id,
                name=name,
                description=description,
                price=price,
                duration_days=durationDays,
                currency=currency,
                features=features,
                is_active=isActive,
                trial_days=trialDays,
            )
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception(f"Database error occurred while creating the plan. {sae}") from sae
        except Exception as e:
            raise Exception(f"An unexpected error occurred while creating the plan. {e}") from e

    @strawberry.mutation
    async def updatePlan(
        self,
        id: int,
        name: str,
        description: str,
        price: float,
        duration_days: int,
        currency: str,
        features: str,
        is_active: bool,
        trial_days: int,
        info
    ) -> SubscriptionPlansResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the existing plan
            plan = await db.get(SubscriptionPlans, id)
            if not plan:
                raise ValidationError(f"Plan with ID {id} not found.")

            # Validate at least one field is being updated
            if not any([name, price, duration_days]):
                raise ValidationError("At least one field must be provided for update.")

            # Update fields
            if name is not None:
                plan.name = name
            if description is not None:
                plan.description = description
            if price is not None:
                plan.price = price
            if duration_days is not None:
                plan.duration_days = duration_days
            if currency is not None:
                plan.currency = currency
            if features is not None:
                plan.features = features
            if is_active is not None:
                plan.is_active = is_active
            if trial_days is not None:
                plan.trial_days = trial_days
            # Commit updates
            await db.commit()
            await db.refresh(plan)

            return SubscriptionPlansResponseType(
                id= plan.id,
                name= plan.name,
                description= plan.description,
                price= plan.price,
                duration_days= plan.duration_days,
                currency= plan.currency,
                features= plan.features,
                is_active= plan.is_active,
                trial_days= plan.trial_days,
            )
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while updating the plan.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while updating the plan.") from e

    @strawberry.mutation
    async def deletePlan(self, id: int, info) -> str:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the plan
            plan = await db.get(SubscriptionPlans, id)
            if not plan:
                raise ValidationError(f"Plan with ID {id} not found.")

            # Delete the plan
            await db.delete(plan)
            await db.commit()

            return f"Plan with ID {id} has been successfully deleted."
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while deleting the plan.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while deleting the plan.") from e
    
