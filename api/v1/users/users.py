from fastapi import APIRouter, Depends

from app.controllers import AuthController, UserController
from app.models.user import User
from app.schemas.requests.users import (
    ChangePasswordRequest,
    UpdateProfileRequest,
)
from app.schemas.responses.global_response import GlobalResponse
from app.schemas.responses.users import UserResponse
from core.exceptions import BadRequestException
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired
from core.fastapi.dependencies.current_user import get_current_user
from core.security import PasswordHandler

user_router = APIRouter()

@user_router.get("/users/get-user", dependencies=[Depends(AuthenticationRequired)])
async def get_users(
    current_user: User = Depends(get_current_user),
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    """
    Retrieve the current user's details.

    Args:
        current_user (User): The authenticated user object.
        user_controller (UserController): The user controller instance.

    Returns:
        GlobalResponse: The response object containing user data or an error message.
    """
    try:
        user = await user_controller.get_by_id(current_user.id)
        data = UserResponse.model_validate(user).model_dump()
        return GlobalResponse.get(data=data)
    except Exception as e:
        print(str(e))
        return GlobalResponse.exception()


@user_router.post("/users/change-password", dependencies=[Depends(AuthenticationRequired)])
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    """
    Change the password of the authenticated user.

    Args:
        request (ChangePasswordRequest): The request body containing the old and new passwords.
        current_user (User): The authenticated user object.
        auth_controller (AuthController): The authentication controller instance.
        user_controller (UserController): The user controller instance.

    Returns:
        GlobalResponse: The response object indicating the result of the password change operation.
    """
    try:
        await auth_controller.login(
            email=current_user.email, password=request.old_password
        )
        password = PasswordHandler.hash(request.password)
        user = await user_controller.update(current_user.id, {"password": password})
        data = UserResponse.model_validate(user).model_dump()
        return GlobalResponse.update(data=data)
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception:
        return GlobalResponse.exception()


@user_router.put("/users/update-profile", dependencies=[Depends(AuthenticationRequired)])
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
    user_controller: UserController = Depends(Factory().get_user_controller),
):
    """
    Update the profile of the authenticated user.

    Args:
        request (UpdateProfileRequest): The request body containing updated profile information.
        current_user (User): The authenticated user object.
        auth_controller (AuthController): The authentication controller instance.
        user_controller (UserController): The user controller instance.

    Returns:
        GlobalResponse: The response object indicating the result of the profile update operation.
    """
    try:
        password = PasswordHandler.hash(request.password)
        user = await user_controller.update(current_user.id, {"password": password, "email": request.email})
        data = UserResponse.model_validate(user).model_dump()
        return GlobalResponse.update(data=data)
    except BadRequestException as e:
        return GlobalResponse.bad_request(message=str(e))
    except Exception:
        return GlobalResponse.exception()
