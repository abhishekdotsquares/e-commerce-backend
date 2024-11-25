import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import AsyncMock, MagicMock

from api.v1.subscription_plans.Mutation.mutation import PlanMutation
from app.models.subscriptionPlans import SubscriptionPlans
from app.schemas.responses.response_types import SubscriptionPlansResponseType

@pytest.mark.asyncio
async def test_create_plan_success():
    # Arrange
    db_mock = AsyncMock()
    db_mock.get.return_value = None  # Simulate no existing plan
    db_mock.add.return_value = None
    db_mock.commit.return_value = None
    db_mock.refresh.return_value = None

    # Mock GraphQLResolveInfo
    mock_info = MagicMock()
    mock_info.context = {"db": db_mock}  # Add mock database to the context

    plan_mutation = PlanMutation()

    # Act
    response = await plan_mutation.createPlan(
        id=1,
        name="Basic Plan",
        description="A basic subscription plan.",
        price=10.99,
        durationDays=30,
        currency="USD",
        features="Basic Features",
        isActive=True,
        trialDays=7,
        info=mock_info,  # Pass the mocked info
    )

    # Assert
    assert response == SubscriptionPlansResponseType(
        id=1,
        name="Basic Plan",
        description="A basic subscription plan.",
        price=10.99,
        duration_days=30,
        currency="USD",
        features="Basic Features",
        is_active=True,
        trial_days=7,
    )
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()
