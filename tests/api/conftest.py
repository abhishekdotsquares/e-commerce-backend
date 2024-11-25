import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import core.database.transactional as transactional
from app.models import Base
# from core.config import config

TEST_DATABASE_URL = os.getenv("NEON_DB_HOST")

# Override the config to use the test database
# config.SQLITE_URL = TEST_DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    # async_engine = create_async_engine(config.SQLITE_URL)
    async_engine = create_async_engine(TEST_DATABASE_URL)
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        transactional.session = s
        yield s

    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     pass

    await async_engine.dispose()
