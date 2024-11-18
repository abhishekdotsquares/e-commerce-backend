from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import uuid
from app.models.company import Company  # Assuming you have the SQLAlchemy model here
from app.schemas.requests.companies import CompanyCreate  # Input schema for creating a company
from app.schemas.responses.companies import CompanyResponse  # Output schema for response
from core.database import session  # Assuming you have a utility to get DB session
from sqlalchemy.orm import selectinload

class CompanyController:
    def __init__(self):
        pass

    async def create_company(self, db: AsyncSession, company: CompanyCreate) -> CompanyResponse:
        """
        Creates a new company record in the database.

        Args:
            db (AsyncSession): Database session for async operations.
            company (CompanyCreate): The company data to be created.

        Returns:
            CompanyResponse: The created company object as response schema.
        """
        # Check if the email already exists in the database (async check)
        result = await db.execute(select(Company).filter(Company.email == company.email))
        existing_company = result.scalars().first()
        if existing_company:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create a new company instance using the Company model
        db_company = Company(
            uuid=uuid.uuid4(),  # Generate a new UUID
            business_name=company.business_name,
            website_link=company.website_link,
            first_name=company.first_name,
            last_name=company.last_name,
            email=company.email,
            phone_number=company.phone_number,
        )

        # Add the new company to the session and commit it to the database
        db.add(db_company)
        await db.commit()  # Use async commit
        await db.refresh(db_company)  # Refresh the instance to get the newly generated ID
        
        # Return the created company in the response format (CompanyResponse)
        return CompanyResponse.from_orm(db_company)
