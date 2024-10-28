import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterUserRequest(BaseModel):
    """
    Pydantic model for registering a new user.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password, which must meet specific criteria.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("password")
    def password_must_contain_special_characters(cls, v):
        """
        Validator to ensure the password contains at least one special character.

        Raises:
            ValueError: If the password does not contain special characters.
        """
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Password must contain special characters")
        return v

    @field_validator("password")
    def password_must_contain_numbers(cls, v):
        """
        Validator to ensure the password contains at least one number.

        Raises:
            ValueError: If the password does not contain numbers.
        """
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain numbers")
        return v

    @field_validator("password")
    def password_must_contain_uppercase(cls, v):
        """
        Validator to ensure the password contains at least one uppercase letter.

        Raises:
            ValueError: If the password does not contain uppercase characters.
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase characters")
        return v

    @field_validator("password")
    def password_must_contain_lowercase(cls, v):
        """
        Validator to ensure the password contains at least one lowercase letter.

        Raises:
            ValueError: If the password does not contain lowercase characters.
        """
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase characters")
        return v


class LoginUserRequest(BaseModel):
    """
    Pydantic model for logging in a user.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
    """
    email: EmailStr
    password: str


class ChangePasswordRequest(RegisterUserRequest):
    """
    Pydantic model for changing a user's password.

    Inherits from RegisterUserRequest and adds attributes for old password.

    Attributes:
        email (str, optional): The user's email address.
        old_password (str): The user's current password.
    """
    email: str = Field(None)
    old_password: str = Field(..., min_length=8, max_length=64)
    password: str = Field(..., min_length=8, max_length=64)


class RefreshTokenRequest(BaseModel):
    """
    Pydantic model for refreshing authentication tokens.

    Attributes:
        access_token (str): The current access token.
        refresh_token (str): The current refresh token.
    """
    access_token: str
    refresh_token: str


class UpdateProfileRequest(RegisterUserRequest):
    """
    Pydantic model for updating a user's profile information.

    Inherits from RegisterUserRequest and adds optional attributes for email and password.

    Attributes:
        email (Optional[EmailStr]): The user's new email address.
        password (Optional[str]): The user's new password.
    """
    email: Optional[EmailStr] = Field(None, description="User's email address")
    password: Optional[str] = Field(None, min_length=8, max_length=64, description="User's new password")


class ForgetPasswordRequest(BaseModel):
    """
    Pydantic model for requesting a password reset.

    Attributes:
        email (EmailStr): The user's email address.
    """
    email: EmailStr = Field(..., description="User's email address")
    
class ResetPasswordRequest(RegisterUserRequest):
    """
    Pydantic model for resetting a user's password.

    Inherits from RegisterUserRequest and adds a reset token.

    Attributes:
        token (str): The reset token sent to the user's email.
    """
    token: str = Field(..., description="Reset token sent to the user's email")
