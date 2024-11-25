import pytest
from httpx import AsyncClient
from core.server import app  # Replace with the path to your FastAPI/Strawberry app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database import Base
import os

from core.server import get_context

DATABASE_URL = os.getenv("DATABASE_URL")  # In-memory SQLite for testing

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(test_engine):
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture(scope="function")
async def client(db_session):
    # Override dependency to inject the test session
    async def override_get_context():
        return {"db": db_session}
    
    app.dependency_overrides[get_context] = override_get_context
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
