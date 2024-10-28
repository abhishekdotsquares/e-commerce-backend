from fastapi import APIRouter, Depends,Header,Request

from app.controllers import AuthController, UserController
from app.schemas.extras.token import Token
from app.schemas.requests.users import LoginUserRequest,ResetPasswordRequest,RegisterUserRequest, ForgetPasswordRequest,ChangePasswordRequest, RefreshTokenRequest,UpdateProfileRequest
from app.schemas.responses.users import UserResponse
from app.schemas.responses.global_response import GlobalResponse
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired
from core.fastapi.dependencies.current_user import get_current_user
from app.models.user import User
from core.security import PasswordHandler,TokenHandler
from core.exceptions import BadRequestException
from typing import Optional
import hashlib


auth_router = APIRouter()



@auth_router.post("/auth/register-user")
async def register_user(
    register_user_request: RegisterUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
):
    try:
        user = await auth_controller.register(
            email=register_user_request.email,
            password=register_user_request.password,
        )
        data = UserResponse.model_validate(user).model_dump()
        return GlobalResponse.create(data=data)
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception:
        return GlobalResponse.exception()


@auth_router.post("/auth/login")
async def login_user(
    login_user_request: LoginUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> GlobalResponse:
    try:
        token = await auth_controller.login(
            email=login_user_request.email, password=login_user_request.password
        )
        data = Token.model_validate(token).model_dump()
        return GlobalResponse.get(data=data)
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception:
        return GlobalResponse.exception()


@auth_router.post("/auth/logout", dependencies=[Depends(AuthenticationRequired)])
async def logout_user(
    request: Request,
    authorization: Optional[str] = Header(None),  # Capture token from the Authorization header
    current_user: User = Depends(get_current_user),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
):
    try:
        
        # Extract the token (if any) from the Authorization header
        token = authorization.replace("Bearer ", "") if authorization else None

        # Call the logout method in your AuthController
        await auth_controller.logout(token)
        
        # Optionally, you might want to inform the client to delete the token
        return GlobalResponse.success(message="Logout successful.")
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception as e:
        return GlobalResponse.exception()



@auth_router.post("/auth/token-refresh")
async def token_refresh(
    refresh_request: RefreshTokenRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
):
    try:
        token = await auth_controller.refresh_token(
            access_token=refresh_request.access_token, refresh_token=refresh_request.refresh_token
        )
        data = Token.model_validate(token).model_dump()
        return GlobalResponse.get(data=data)
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception as e:
        return GlobalResponse.bad_request(message=str(e))


@auth_router.post("/auth/forget-password")
async def forget_password(
    request: ForgetPasswordRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    try:
        user = await user_controller.get_by_email(request.email)
        if not user:
            return GlobalResponse.bad_request( message="User not found")

        # Generate the reset token based on UUID and email
        reset_token = TokenHandler.generate_reset_token(request.email)

        # Optionally, you could send the reset token to the user's email
        # await auth_controller.send_reset_email(request.email, reset_token)

        return GlobalResponse.get(data={"reset_token": reset_token})

    except Exception as e:
        return GlobalResponse.exception()
    
    
@auth_router.post("/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    try:
        # Here you would normally check if the token is valid in some way
        if not TokenHandler.validate_reset_token(request.token, request.email):
            return GlobalResponse.bad_request( message="Token is not matched")
        
        user = await user_controller.get_by_email(request.email)

        # Proceed to reset the password
        hashed_password = PasswordHandler.hash(request.password)
        await user_controller.update(user.id, {"password": hashed_password})

        return GlobalResponse.get(data={"message": "Password reset successfully"})

    except Exception as e:
        return GlobalResponse.exception()
