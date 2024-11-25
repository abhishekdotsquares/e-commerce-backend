from datetime import datetime, timedelta, timezone
from uuid import uuid4
import strawberry
from app.models.passwordResetToken import PasswordResetToken
from app.models.user import User
from app.schemas.requests.request_types import UserRequestType
from app.schemas.responses.response_types import ForgotPasswordResponseType, UserResponseType,TokenType
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
    ) -> UserRequestType:
        db: AsyncSession = info.context['db']

        try:
            # Validate inputs
            if not email or not password or is_superuser is None:
                raise ValidationError("All fields are required.")
            
            # Check if the user already exists
            result = await db.execute(select(User).where(User.email == email))
            if result.raw.rowcount > 0:
                raise ValidationError(f"User with email {email} already exists.")


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

            # Return the user response without the password
            return UserResponseType(
                id=new_user.id,
                email=new_user.email,
                password=new_user.password,
                is_superuser=new_user.is_superuser,
            )
        except ValidationError as ve:
            raise ve
        except SQLAlchemyError as sae:
            await db.rollback()
            raise Exception("Database error occurred while creating the user.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while creating the user.") from e

    @strawberry.mutation
    async def loginUser(
        self,
        email: str,
        password: str,
        info,
    ) -> TokenType:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the user from the database
            user = await db.scalar(
            select(User).where(User.email == email)
            )

            if not user:
                raise BadRequestException("Invalid email or password.")

            # Verify the password
            if not pwd_context.verify(password, user.password):
                raise BadRequestException("Invalid email or password.")

            access_token=JWTHandler.encode(payload={"user_id": user.id}),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
            
          
            return TokenType(
                access_token=access_token[0],
                token_type="bearer",
                refresh_token=refresh_token[0],
            )

        except BadRequestException as e:
            raise e
        except SQLAlchemyError as sae:
            raise Exception("Database error occurred while logging in.") from sae
        except Exception as e:
            raise Exception("An unexpected error occurred while logging in.") from e

    @strawberry.mutation
    async def forgotPassword(
        self,
        email: str,
        info,
    ) -> ForgotPasswordResponseType:
        db: AsyncSession = info.context['db']

        try:
            # Fetch the user by email
            async with db.begin():  # Ensure a properly scoped transaction
                user = await db.scalar(select(User).where(User.email == email))



            if not user:
                # Avoid revealing email validity for security
                return ForgotPasswordResponseType(
                    success=False,
                    message="User not found."
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

            # Respond to user
            return ForgotPasswordResponseType(
                success=True,
                message="Email sent successfully, you will receive a password reset link shortly."
            )

        except Exception as e:
            raise Exception("An unexpected error occurred while processing the forgot password request.") from e
    
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
                    success=False,
                    message="Invalid or expired token."
                )

            # Step 2: Check if the token is expired
            if reset_entry.expires_at < datetime.now(timezone.utc):
                return ForgotPasswordResponseType(
                    success=False,
                    message="The reset token has expired. Please request a new one."
                )

            # Step 3: Fetch the associated user
            async with db.begin():
                user = await db.get(User, reset_entry.user_id)

            if not user:
                return ForgotPasswordResponseType(
                    success=False,
                    message="User associated with the reset token not found."
                )

            # Step 4: Hash the new password
            hashed_password = pwd_context.hash(new_password)

            # Step 5: Update the user's password
            async with db.begin():
                user.password = hashed_password
                db.add(user)
                # Invalidate the reset token by deleting it
                await db.delete(reset_entry)
                await db.commit()

            return ForgotPasswordResponseType(
                success=True,
                message="Password has been reset successfully. You can now log in with your new password."
            )

        except Exception as e:
            raise Exception("An unexpected error occurred while resetting the password.") from e
