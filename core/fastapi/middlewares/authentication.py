from typing import Optional, Tuple

from jose import JWTError, jwt
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection

from app.schemas.extras.current_user import CurrentUser
# from core.config import config
import os 


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()

        authorization: str = conn

        if not authorization:
            return False

        try:
            scheme, token = authorization.split(" ")
            if scheme.lower() != "bearer":
                return False, current_user
        except ValueError:
            return False, current_user

        if not token:
            return False, current_user

        try:
            payload = jwt.decode(
                token,
                os.getenv('SECRET_KEY'),
                algorithms=[os.getenv('JWT_ALGORITHM')],
            )
            user_id = payload.get("user_id")
        except JWTError:
            return False, current_user

        current_user.id = user_id
        return True


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
