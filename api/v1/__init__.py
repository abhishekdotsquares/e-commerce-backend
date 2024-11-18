from fastapi import APIRouter
from .users import users_router
from .companies import companies_router

v1_router = APIRouter()
v1_router.include_router(users_router)
v1_router.include_router(companies_router)
