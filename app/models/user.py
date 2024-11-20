from uuid import uuid4

from sqlalchemy import Column, Integer, String, Unicode,Boolean
from sqlalchemy.ext.declarative import declarative_base

from core.database import Base
from core.database.mixins import TimestampMixin

# Base = declarative_base()


class User(Base, TimestampMixin):
    """
    User model representing the 'users' table in the database.

    Attributes:
        id (int): Primary key, auto-incremented identifier for the user.
        uuid (str): Unique identifier for the user, generated using UUID.
        email (str): Email address of the user, must be unique.
        password (str): Hashed password of the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid4()), unique=True, nullable=False)
    email = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    is_superuser = Column(Boolean,default=False, nullable=False)

    __mapper_args__ = {"eager_defaults": True}
