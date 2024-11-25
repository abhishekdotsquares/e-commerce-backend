from strawberry.types import Info
from jose import jwt
from fastapi import HTTPException, Request
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")


class JwtAuthMiddleware:
    """
    Middleware to authenticate JWT and attach user data to the context.
    """

    async def resolve(self, next_resolver, root, info: Info, *args, **kwargs):
        # Access the HTTP request object
        request: Request = info.context["request"]

        # Extract token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        token = auth_header.split(" ")[1]

        try:
            # Validate the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            if not user_email:
                raise HTTPException(status_code=401, detail="Invalid token: missing subject")

            # Attach user info to the context
            info.context["user"] = {"email": user_email}  # Add other claims as necessary

            # Proceed to the resolver
            return await next_resolver(root, info, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")
