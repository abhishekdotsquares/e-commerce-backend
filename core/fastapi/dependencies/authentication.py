from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.controllers.auth import BLACKLIST
from core.config import config
from core.exceptions.base import CustomException


class AuthenticationRequiredException(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication required"


class AuthenticationRequired:
    def __init__(
        self,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ):
        if not token:
            raise AuthenticationRequiredException()
        try:

            if token.credentials in BLACKLIST:
                raise AuthenticationRequiredException()
             
            jwt.decode(
                token.credentials,
                config.SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
        except JWTError:
            raise AuthenticationRequiredException()
        except Exception:
            raise AuthenticationRequiredException()
