from fastapi import APIRouter

from .companies import company_router


companies_router = APIRouter()
companies_router.include_router(company_router, tags=["Company"])

__all__ = ["companies_router"]
