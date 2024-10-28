from fastapi import APIRouter

from .users import user_router
from .auth import auth_router


users_router = APIRouter()
users_router.include_router(user_router, tags=["Users"])
users_router.include_router(auth_router, tags=["Auth"])

__all__ = ["users_router"]
