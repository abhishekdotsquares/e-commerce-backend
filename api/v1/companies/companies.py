from http.client import HTTPException
from app.controllers.company import CompanyController
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.schemas.responses.companies import CompanyResponse
from app.schemas.requests.companies import CompanyCreate

from core.exceptions import BadRequestException
from core.factory import Factory
import uuid
from core.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

company_router = APIRouter()
@company_router.post("/companies/create-company", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,  # Input schema for creating a company
    db: AsyncSession = Depends(get_db),  # Use async session from dependency
    company_controller: CompanyController = Depends(CompanyController)  # Injecting controller
):
    """
    Endpoint to create a new company.

    Args:
        company (CompanyCreate): Company data from the request body.
        db (AsyncSession): The database session dependency.
        company_controller (CompanyController): The controller for handling the business logic.

    Returns:
        CompanyResponse: The created company object.
    """
    try:
        db_company = await company_controller.create_company(db=db, company=company)
        return db_company  # Return the created company as a response model
    except HTTPException as e:
        raise e  # Re-raise HTTPException if email already exists or any other error
