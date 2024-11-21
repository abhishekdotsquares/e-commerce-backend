from uuid import uuid4
from sqlalchemy import Column, Integer, String, Unicode, DateTime, Text, Float, JSON, Boolean
from core.database import Base
from core.database.mixins import TimestampMixin
from sqlalchemy import func
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base = declarative_base()


class SubscriptionPlans(Base,TimestampMixin):
    __tablename__ = 'subscription_plans'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)  # E.g., 30 for monthly, 365 for yearly
    currency = Column(String(10), nullable=False, default="USD")
    features = Column(JSON, nullable=True)  # Optional: JSON to store features
    trial_days = Column(Integer, nullable=True, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  
    deleted_at = Column(DateTime, nullable=True) 

    # Relationship with subscriptions
    subscriptions = relationship("companyPlanAssociations", back_populates="plan")
    __mapper_args__ = {"eager_defaults": True}

