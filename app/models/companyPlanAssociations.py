from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from core.database import Base
from sqlalchemy import func


class companyPlanAssociations(Base):
    __tablename__ = "company_subscribed_plans"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)

    # Foreign key references the company table
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Foreign key references the subscription plan table
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)

    # Subscription related data
    start_date = Column(DateTime, server_default=func.now(), nullable=False)  
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  
    deleted_at = Column(DateTime, nullable=True) 
    # Relationship with other tables (optional)
    company = relationship("Company", back_populates="subscriptions")
    plan = relationship("SubscriptionPlans", back_populates="subscriptions")

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f"<CompanySubscribedPlan(company_id={self.company_id}, plan_id={self.plan_id}, start_date={self.start_date}, is_active={self.is_active})>"
