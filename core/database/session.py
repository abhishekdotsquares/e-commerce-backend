from contextvars import ContextVar, Token
from typing import Union
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.expression import Update, Delete, Insert
from core.config import config as app_config
from core.database.db import SessionLocal
# Context variable to manage session context
session_context: ContextVar[str] = ContextVar("session_context")

# Database URL for Neon (assuming config holds the actual connection string)
neon_db_url = app_config.NEON_DB_HOST

# Engines for writer and reader
engines = {
    "writer": create_async_engine(neon_db_url, pool_recycle=3600),
    "reader": create_async_engine(neon_db_url, pool_recycle=3600),
}

# Routing session that determines whether to use the reader or writer engine
class RoutingSession(AsyncSession):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        # If it's a write operation (flushing or a mutating clause), use the writer engine
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"]
        # Otherwise, use the reader engine
        return engines["reader"]

# Create sessionmaker using the custom routing session class
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)

# Scoped session to handle async context
session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=AsyncSessionLocal,
    scopefunc=session_context.get,
)

# Create a base class for declarative models (models will inherit from this)
Base = declarative_base()
from sqlalchemy.ext.asyncio import AsyncSession
# Dependency to inject the session into FastAPI routes
async def get_db():
    async with SessionLocal() as session:
        yield session

# Dependency to get a session (for other cases where you need manual control)
async def get_session():
    """
    This function provides the database session to be used manually.
    """
    async with session() as db:
        yield db

# Set the session context
def set_session_context(session_id: str) -> Token:
    """
    Set the session context to the provided session ID.
    This is used to track the session for each request.
    """
    return session_context.set(session_id)

# Reset the session context
def reset_session_context(context: Token) -> None:
    """
    Reset the session context after the request is completed.
    This clears the session context and prevents any data from leaking
    between requests.
    """
    session_context.reset(context)
