from uuid import uuid4

from sqlalchemy import Integer, Column, Unicode, String
from core.database import Base
from core.database.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid4()), unique=True, nullable=False)
    email = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    # reset_token = Column(String(36), default=lambda: str(uuid4()), unique=True, nullable=False)

    __mapper_args__ = {"eager_defaults": True}

