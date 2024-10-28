from fastapi import APIRouter, Depends, Header, Request

from app.controllers import AuthController, UserController
from app.schemas.extras.token import Token
from app.schemas.requests.users import (
    LoginUserRequest,
    ResetPasswordRequest,
    RegisterUserRequest,
    ForgetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    UpdateProfileRequest,
)
from app.schemas.responses.users import UserResponse
from app.schemas.responses.global_response import GlobalResponse
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired
from core.fastapi.dependencies.current_user import get_current_user
from app.models.user import User
from core.security import PasswordHandler, TokenHandler
from core.exceptions import BadRequestException
from typing import Optional

auth_router = APIRouter()

@auth_router.post("/auth/register-user")
async def register_user(
    register_user_request: RegisterUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
):
    """
    Register a new user.

    Args:
        register_user_request (RegisterUserRequest): The request body containing user registration details.

    Returns:
        GlobalResponse: The response object indicating the result of the registration operation.
    """
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
    """
    Log in a user and return an authentication token.

    Args:
        login_user_request (LoginUserRequest): The request body containing login credentials.

    Returns:
        GlobalResponse: The response object containing the authentication token or an error message.
    """
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
    """
    Log out the authenticated user.

    Args:
        request (Request): The FastAPI request object.
        authorization (Optional[str]): The token extracted from the Authorization header.
        current_user (User): The authenticated user object.
        auth_controller (AuthController): The authentication controller instance.

    Returns:
        GlobalResponse: The response object indicating the success of the logout operation.
    """
    try:
        # Extract the token (if any) from the Authorization header
        token = authorization.replace("Bearer ", "") if authorization else None

        # Call the logout method in your AuthController
        await auth_controller.logout(token)

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
    """
    Refresh the user's authentication token.

    Args:
        refresh_request (RefreshTokenRequest): The request body containing the access and refresh tokens.

    Returns:
        GlobalResponse: The response object containing the new tokens or an error message.
    """
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
    """
    Initiate the password reset process by generating a reset token.

    Args:
        request (ForgetPasswordRequest): The request body containing the email of the user.

    Returns:
        GlobalResponse: The response object containing the reset token or an error message.
    """
    try:
        user = await user_controller.get_by_email(request.email)
        if not user:
            return GlobalResponse.bad_request(message="User not found")

        # Generate the reset token based on UUID and email
        reset_token = TokenHandler.generate_reset_token(request.email)

        return GlobalResponse.get(data={"reset_token": reset_token})

    except Exception as e:
        return GlobalResponse.exception()


@auth_router.post("/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    """
    Reset the user's password using the reset token.

    Args:
        request (ResetPasswordRequest): The request body containing the email, new password, and reset token.

    Returns:
        GlobalResponse: The response object indicating the success of the password reset operation.
    """
    try:
        # Validate the reset token
        if not TokenHandler.validate_reset_token(request.token, request.email):
            return GlobalResponse.bad_request(message="Token is not matched")

        user = await user_controller.get_by_email(request.email)

        # Proceed to reset the password
        hashed_password = PasswordHandler.hash(request.password)
        await user_controller.update(user.id, {"password": hashed_password})

        return GlobalResponse.get(data={"message": "Password reset successfully"})

    except Exception as e:
        return GlobalResponse.exception()
