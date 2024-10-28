from httpx import AsyncClient

from tests.factory.users import create_fake_user


async def _create_user_and_login(
    client: AsyncClient
) -> None:
    fake_user = create_fake_user()

    await client.post("/api/v1/auth/register-user", json=fake_user)

    response = await client.post("/api/v1/auth/login", json=fake_user)
    access_token = response.json()["data"]["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    return None


__all__ = ["_create_user_and_login"]
