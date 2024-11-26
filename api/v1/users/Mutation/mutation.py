from datetime import datetime, timedelta, timezone
from uuid import uuid4
import strawberry
from api.v1.response_utils import build_response
from app.models.passwordResetToken import PasswordResetToken
from app.models.user import User
from app.schemas.responses.response_types import CommonResponseType, ForgotPasswordResponseType, LoginResponseType, UserResponseType,TokenType
from core.exceptions import BadRequestException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from core.security.jwt import JWTHandler
from core.utils.email import send_email
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def createUser(
        self,
        email: str,
        password: str,
        is_superuser: bool,
        info,
    ) -> CommonResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not email or not password or is_superuser is None:
                return build_response(
                    response_type=CommonResponseType,
                    message="All fields are required.",
                    status=False,
                    data=None
                )
            
            # Check if the user already exists
            result = await db.execute(select(User).where(User.email == email))
            if result.raw.rowcount > 0:
                return build_response(
                    response_type=CommonResponseType,
                    message=f"User with email {email} already exists.",
                    status=False,
                    data=None
                )

            # Hash the password
            hashed_password = pwd_context.hash(password)

            # Create the user in the database
            new_user = User(
                email=email,
                password=hashed_password,
                is_superuser=is_superuser,
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return build_response(
                response_type=CommonResponseType,
                message="User created successfully.",
                status=True,
                data=None
            )
        except SQLAlchemyError as sae:
            await db.rollback()
            return build_response(
                response_type=CommonResponseType,
                message="Database error occurred while creating the user.",
                status=False,
                data=None
            )
        except Exception as e:
            return build_response(
                response_type=CommonResponseType,
                message="An unexpected error occurred while creating the user.",
                status=False,
                data=None
            )

    @strawberry.mutation
    async def loginUser(
        self,
        email: str,
        password: str,
        info,
    ) -> CommonResponseType:
        db: AsyncSession = info.context['db']
        
        try:
            # Fetch the user from the database
            user = await db.scalar(
                select(User).where(User.email == email)
            )

            if not user:
                return build_response(
                    response_type=CommonResponseType,
                    message="Invalid email or password.",
                    status=False,
                    data=None
                )
            # Verify the password
            if not pwd_context.verify(password, user.password):
                return build_response(
                    response_type=CommonResponseType,
                    message="Invalid email or password.",
                    status=False,
                    data=None
                )

            access_token = JWTHandler.encode(payload={"user_id": user.id}),
            refresh_token = JWTHandler.encode(payload={"sub": "refresh_token"}),
            return build_response(
                    response_type=CommonResponseType,
                    message="Login Successfully",
                    status=True,
                    data={
                    "access_token":access_token[0],
                    "refresh_token":refresh_token[0],
                    }
                )
        except BadRequestException as e:
            return build_response(
                response_type=CommonResponseType,
                message=str(e),
                status=False,
                data=None
            )
        except SQLAlchemyError as sae:
            return build_response(
                response_type=CommonResponseType,
                message="Database error occurred while logging in.",
                status=False,
                data=None
            )
        except Exception as e:
            return build_response(
                response_type=CommonResponseType,
                message="An unexpected error occurred while logging in.",
                status=False,
                data=None
            )

    @strawberry.mutation
    async def forgotPassword(
        self,
        email: str,
        info,
    ) -> CommonResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return build_response(
                    response_type=CommonResponseType,
                    message="Invalid email format.",
                    status=False,
                    data=None
                )
            # Fetch the user by email
            async with db.begin():  # Ensure a properly scoped transaction
                user = await db.scalar(select(User).where(User.email == email))

            if not user:
                # Avoid revealing email validity for security
                return build_response(
                    response_type=CommonResponseType,
                    message="Email doesn't exists.Please Sign Up.",
                    status=False,
                    data=None
                )

            # Generate reset token
            reset_token = str(uuid4())
            token_expiry = datetime.now(timezone.utc) + timedelta(minutes=15)

            # Save reset token in the database
            async with db.begin():
                reset_entry = PasswordResetToken(
                    user_id=user.id,
                    token=reset_token,
                    expires_at=token_expiry
                )
                db.add(reset_entry)
                await db.commit()

            # Send reset email
            reset_link = f"https://192.168.9.230:3000/reset-password?token={reset_token}"
            user_email = user.email
            email_body = f"""
            <p>Hi {user_email},</p>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request this, please ignore this email.</p>
            """
            await send_email(
                to_email=user.email,
                subject="Password Reset Request",
                body=email_body,
            )
            return build_response(
                response_type=CommonResponseType,
                message="Reset Password link sent successfully.",
                status=True,
                data=None
            )
        except SQLAlchemyError as sae:
            # Handle any database-related errors
            return build_response(
                response_type=CommonResponseType,
                message="Database error occurred while processing your request.",
                status=False,
                data=None
            )
        except Exception as e:
            # Handle unexpected errors
            return build_response(
                response_type=CommonResponseType,
                message="An unexpected error occurred while processing the forgot password request.",
                status=False,
                data=None
            )

    
    @strawberry.mutation
    async def resetPassword(
        self,
        token: str,
        new_password: str,
        info,
    ) -> CommonResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Step 1: Fetch the reset token record from the database
            async with db.begin():
                reset_entry = await db.scalar(
                    select(PasswordResetToken).where(PasswordResetToken.token == token)
                )

            if not reset_entry:
                return build_response(
                    response_type=CommonResponseType,
                    message="Invalid or expired token.",
                    status=False,
                    data=None
                )

            # Step 3: Check if the token is expired
            if reset_entry.expires_at < datetime.now(timezone.utc):
                return build_response(
                    response_type=CommonResponseType,
                    message="The reset token has expired. Please request a new one.",
                    status=False,
                    data=None
                )
            # Step 4: Fetch the associated user
            async with db.begin():
                user = await db.get(User, reset_entry.user_id)

            if not user:
                return build_response(
                    response_type=CommonResponseType,
                    message="User associated with the reset token not found.",
                    status=False,
                    data=None
                )

            # Step 5: Validate the new password (for example, minimum length and complexity)
            if len(new_password) < 8:
                return build_response(
                    response_type=CommonResponseType,
                    message="Password must be at least 8 characters long.",
                    status=False,
                    data=None
                )
                
            if not re.search(r"[A-Z]", new_password):  # At least one uppercase letter
                return build_response(
                    response_type=CommonResponseType,
                    message="Password must contain at least one uppercase letter.",
                    status=False,
                    data=None
                )

            if not re.search(r"[a-z]", new_password):  # At least one lowercase letter
                return build_response(
                    response_type=CommonResponseType,
                    message="Password must contain at least one lowercase letter.",
                    status=False,
                    data=None
                )

            if not re.search(r"[0-9]", new_password):  # At least one digit
                return build_response(
                    response_type=CommonResponseType,
                    message="Password must contain at least one digit.",
                    status=False,
                    data=None
                )

            # Step 6: Hash the new password
            hashed_password = pwd_context.hash(new_password)

            # Step 7: Update the user's password
            async with db.begin():
                user.password = hashed_password
                db.add(user)
                # Invalidate the reset token by deleting it
                await db.delete(reset_entry)
                await db.commit()
            return build_response(
                response_type=CommonResponseType,
                message="Password has been reset successfully. You can now log in with your new password.",
                status=True,
                data=None
            )

        except SQLAlchemyError as sae:
            # Handle any database-related errors
            return build_response(
                response_type=CommonResponseType,
                message="Database error occurred while resetting your password.",
                status=False,
                data=None
            )
        except Exception as e:
            # Handle unexpected errors
            return build_response(
                response_type=CommonResponseType,
                message="An unexpected error occurred while resetting the password.",
                status=False,
                data=None
            )