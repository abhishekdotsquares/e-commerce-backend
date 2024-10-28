import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("password")
    def password_must_contain_special_characters(cls, v):
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Password must contain special characters")
        return v

    @field_validator("password")
    def password_must_contain_numbers(cls, v):
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain numbers")
        return v

    @field_validator("password")
    def password_must_contain_uppercase(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase characters")
        return v

    @field_validator("password")
    def password_must_contain_lowercase(cls, v):
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase characters")
        return v


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(RegisterUserRequest):
    email: str = Field(None)
    old_password: str = Field(..., min_length=8, max_length=64)
    password: str = Field(..., min_length=8, max_length=64)


class RefreshTokenRequest(BaseModel):
    access_token: str
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, description="User's email address")
    # password: Optional[str] = Field(None, min_length=8, max_length=64, description="User's new password")

class ForgetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    
class ResetPasswordRequest(RegisterUserRequest):
    token: str = Field(..., description="Reset token sent to the user's email")
   
