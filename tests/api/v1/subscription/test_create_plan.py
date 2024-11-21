import pytest
from httpx import AsyncClient
import os

from tests.factory.plans import create_fake_plan


@pytest.mark.asyncio
async def test_create_plan(client: AsyncClient) -> None:
    """Test plan creation."""
    fake_plan = create_fake_plan()
    # Define the GraphQL mutation
    mutation = f"""
    mutation {{
        createPlan(
            id: {fake_plan['id']},
            name: "{fake_plan['name']}",
            description: "{fake_plan['description']}",
            price: {fake_plan['price']},
            durationDays: {fake_plan['durationDays']},
            currency: "{fake_plan['currency']}",
            features: "{fake_plan['features']}",
            isActive: {str(fake_plan['isActive']).lower()},
            trialDays: {fake_plan['trialDays']}
        ) {{
            id
            name
            price
            durationDays
            currency
            features
            isActive
            trialDays
        }}
    }}
    """

    # Send the GraphQL request
    BASE_URL = os.getenv("TEST_BASE_URL", "http://0.0.0.0:5010")

    response = await client.post(f"{BASE_URL}/graphql", json={"query": mutation})
    # Assert the response
    assert response.status_code == 200
    data = response.json()
    # Verify that the response data matches the input fake_plan
    assert data["data"]["createPlan"]["id"] == fake_plan["id"]
    assert data["data"]["createPlan"]["name"] == fake_plan["name"]
    assert data["data"]["createPlan"]["price"] == fake_plan["price"]
    assert data["data"]["createPlan"]["duration_days"] == fake_plan["durationDays"]
    assert data["data"]["createPlan"]["currency"] == fake_plan["currency"]
    assert data["data"]["createPlan"]["features"] == fake_plan["features"]
    assert data["data"]["createPlan"]["is_active"] == fake_plan["isActive"]
    assert data["data"]["createPlan"]["trial_days"] == fake_plan["trialDays"]
