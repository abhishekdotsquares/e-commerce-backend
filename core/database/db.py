import databases
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from core.database.base import Base

load_dotenv()

# Make sure to load the correct DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://harmannstudios_owner:OCE4JHxpzl8h@ep-square-dew-a5ke67mm.us-east-2.aws.neon.tech/harmannstudios")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker instance
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Initialize the database and create all tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
