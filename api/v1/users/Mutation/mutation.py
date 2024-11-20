from datetime import datetime, timedelta, timezone
from uuid import uuid4
import strawberry
from app.models.passwordResetToken import PasswordResetToken
from app.models.user import User
from app.schemas.responses.types import ForgotPasswordResponseType, UserResponseType,TokenType
from core.exceptions import BadRequestException
from core.exceptions.validation_error import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from core.utils.email import send_email
from core.utils.generate_token import create_access_token


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
                raise ValidationError("All fields are required.")

            # Check if the user already exists
            existing_user = await db.execute(
                User.__table__.select().filter(User.email == email)
            )
            existing_user = existing_user.scalars().first()

            if existing_user:
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

            # Create a JWT token
            token_data = {"sub": user.email}
            access_token = create_access_token(data=token_data)
            
            refresh_token_data = {"sub": user.email, "scope": "refresh"}
            refresh_token = create_access_token(
                data=refresh_token_data,
                expires_delta=timedelta(days=7),  # Example: 7-day expiry for refresh token
            )
            
            # Return the token response
            return TokenType(
                access_token=access_token,
                token_type="bearer",
                refresh_token=refresh_token,
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
            user = await db.scalar(
                select(User).where(User.email == email)
            )

            if not user:
                # Avoid revealing email validity for security
                return ForgotPasswordResponseType(
                    success=True,
                    message="If the email is registered, you will receive a password reset link shortly."
                )

            # Generate reset token
            reset_token = str(uuid4())
            token_expiry = datetime.now(timezone.utc) + timedelta(minutes=15)

            # Save reset token in the database
            reset_entry = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=token_expiry
            )
            db.add(reset_entry)
            await db.commit()

            # Send reset email
            reset_link = f"https://192.168.9.230:3000/reset-password?token={reset_token}"
            email_body = f"""
            <p>Hi {user.email},</p>
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
                message="If the email is registered, you will receive a password reset link shortly."
            )

        except Exception as e:
            raise Exception("An unexpected error occurred while processing the forgot password request.") from e
