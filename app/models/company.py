from uuid import uuid4

from sqlalchemy import Column, Integer, String, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base

from core.database import Base
from core.database.mixins import TimestampMixin
from sqlalchemy import func



class Company(Base,TimestampMixin):
    __tablename__ = 'companies'
  
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid4()), unique=True, nullable=False) 
    business_name = Column(String(255), nullable=False)
    website_link = Column(String(255), nullable=True)  
    first_name = Column(String(100), nullable=False)  
    last_name = Column(String(100), nullable=False)  
    email = Column(Unicode(255), nullable=False, unique=True)  
    phone_number = Column(String(20), nullable=True)  
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  
    deleted_at = Column(DateTime, nullable=True) 

    __mapper_args__ = {"eager_defaults": True}