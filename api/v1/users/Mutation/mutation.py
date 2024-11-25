from datetime import datetime, timedelta, timezone
from uuid import uuid4
import strawberry
from app.models.passwordResetToken import PasswordResetToken
from app.models.user import User
from app.schemas.requests.request_types import UserRequestType
from app.schemas.responses.response_types import ForgotPasswordResponseType, LoginResponseType, UserResponseType,TokenType
from core.exceptions import BadRequestException
from core.exceptions.validation_error import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from core.security.jwt import JWTHandler
from core.utils.email import send_email
from core.security.token_auth import create_access_token
from sqlalchemy.orm import selectinload
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
    ) -> UserResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not email or not password or is_superuser is None:
                return UserResponseType(
                    status="error",
                    message="All fields are required.",
                )
            
            # Check if the user already exists
            result = await db.execute(select(User).where(User.email == email))
            if result.raw.rowcount > 0:
                return UserResponseType(
                    status="error",
                    message=f"User with email {email} already exists.",
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

            # Return status response
            return UserResponseType(
                status="status",
                message="User created successfully.",
                id=new_user.id,
                email=new_user.email,
                is_superuser=new_user.is_superuser,
            )
        except SQLAlchemyError as sae:
            await db.rollback()
            return UserResponseType(
                status="error",
                message="Database error occurred while creating the user.",
            )
        except Exception as e:
            return UserResponseType(
                status="error",
                message="An unexpected error occurred while creating the user.",
            )

    @strawberry.mutation
    async def loginUser(
        self,
        email: str,
        password: str,
        info,
    ) -> LoginResponseType:
        db: AsyncSession = info.context['db']
        
        try:
            # Fetch the user from the database
            user = await db.scalar(
                select(User).where(User.email == email)
            )

            if not user:
                return LoginResponseType(
                    status=False,
                    message="Invalid email or password.",
                    access_token=None,
                    refresh_token=None
                )

            # Verify the password
            if not pwd_context.verify(password, user.password):
                return LoginResponseType(
                    status=False,
                    message="Invalid email or password.",
                    access_token=None,
                    refresh_token=None
                )

            access_token = JWTHandler.encode(payload={"user_id": user.id}),
            refresh_token = JWTHandler.encode(payload={"sub": "refresh_token"}),

            return LoginResponseType(
                status=True,
                message="Login statusful.",
                access_token=access_token[0],
                refresh_token=refresh_token[0],
            )

        except BadRequestException as e:
            return LoginResponseType(
                status=False,
                message=str(e),
                access_token=None,
                refresh_token=None
            )
        except SQLAlchemyError as sae:
            return LoginResponseType(
                status=False,
                message="Database error occurred while logging in.",
                access_token=None,
                refresh_token=None
            )
        except Exception as e:
            return LoginResponseType(
                status=False,
                message="An unexpected error occurred while logging in.",
                access_token=None,
                refresh_token=None
            )

    @strawberry.mutation
    async def forgotPassword(
        self,
        email: str,
        info,
    ) -> ForgotPasswordResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return ForgotPasswordResponseType(
                    status=False,
                    message="Invalid email format."
                )

            # Fetch the user by email
            async with db.begin():  # Ensure a properly scoped transaction
                user = await db.scalar(select(User).where(User.email == email))

            if not user:
                # Avoid revealing email validity for security
                return ForgotPasswordResponseType(
                    status=False,
                    message="Email doesn't exists.Please Sign Up."
                )

            # # Check if the user has made a recent password reset request (Optional - Throttling)
            # recent_reset = await db.scalar(
            #     select(PasswordResetToken)
            #     .where(PasswordResetToken.user_id == user.id)
            #     .where(PasswordResetToken.expires_at > datetime.now(timezone.utc))
            #     .order_by(PasswordResetToken.expires_at.desc())
            # )

            # if recent_reset:
            #     return ForgotPasswordResponseType(
            #         status=False,
            #         message="A password reset link was already sent recently. Please try again later."
            #     )

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

            # Respond to user
            return ForgotPasswordResponseType(
                status=True,
                message="Reset Password link sent successfully."
            )

        except SQLAlchemyError as sae:
            # Handle any database-related errors
            return ForgotPasswordResponseType(
                status=False,
                message="Database error occurred while processing your request."
            )
        except Exception as e:
            # Handle unexpected errors
            return ForgotPasswordResponseType(
                status=False,
                message="An unexpected error occurred while processing the forgot password request."
            )
    
    @strawberry.mutation
    async def resetPassword(
        self,
        token: str,
        new_password: str,
        info,
    ) -> ForgotPasswordResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Step 1: Fetch the reset token record from the database
            async with db.begin():
                reset_entry = await db.scalar(
                    select(PasswordResetToken).where(PasswordResetToken.token == token)
                )

            if not reset_entry:
                return ForgotPasswordResponseType(
                    status=False,
                    message="Invalid or expired token."
                )

            # Step 3: Check if the token is expired
            if reset_entry.expires_at < datetime.now(timezone.utc):
                return ForgotPasswordResponseType(
                    status=False,
                    message="The reset token has expired. Please request a new one."
                )

            # Step 4: Fetch the associated user
            async with db.begin():
                user = await db.get(User, reset_entry.user_id)

            if not user:
                return ForgotPasswordResponseType(
                    status=False,
                    message="User associated with the reset token not found."
                )

            # Step 5: Validate the new password (for example, minimum length and complexity)
            if len(new_password) < 8:
                return ForgotPasswordResponseType(
                    status=False,
                    message="Password must be at least 8 characters long."
                )
            
            if not re.search(r"[A-Z]", new_password):  # At least one uppercase letter
                return ForgotPasswordResponseType(
                    status=False,
                    message="Password must contain at least one uppercase letter."
                )

            if not re.search(r"[a-z]", new_password):  # At least one lowercase letter
                return ForgotPasswordResponseType(
                    status=False,
                    message="Password must contain at least one lowercase letter."
                )

            if not re.search(r"[0-9]", new_password):  # At least one digit
                return ForgotPasswordResponseType(
                    status=False,
                    message="Password must contain at least one digit."
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

            return ForgotPasswordResponseType(
                status=True,
                message="Password has been reset successfully. You can now log in with your new password."
            )

        except SQLAlchemyError as sae:
            # Handle any database-related errors
            return ForgotPasswordResponseType(
                status=False,
                message="Database error occurred while resetting your password."
            )
        except Exception as e:
            # Handle unexpected errors
            return ForgotPasswordResponseType(
                status=False,
                message="An unexpected error occurred while resetting the password."
            )