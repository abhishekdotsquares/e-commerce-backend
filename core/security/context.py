from functools import cached_property
from fastapi import Request
import strawberry
from app.models import User
from core.security.token_auth import decode_access_token
from strawberry.fastapi import BaseContext
from sqlalchemy.ext.asyncio import AsyncSession

class Context(BaseContext):
    def __init__(self, request: Request, db: AsyncSession):
        self.request = request
        self.db = db
        # self.user = self._get_user_from_token()

    # def _get_user_from_token(self):
    #     pass
    #     # Extract the JWT token from the Authorization header
    #     authorization = self.request.headers.get("Authorization")
    #     print("🐍 File: security/context.py | Line: 18 | _get_user_from_token ~ authorization",authorization)
    #     if authorization and authorization.startswith("Bearer "):
    #         token = authorization.split(" ")[1]
    #         try:
    #             # Decode and verify the JWT token
    #             return decode_access_token(token)
    #         except Exception:
    #             return None  # Invalid or expired token
    #     return None
