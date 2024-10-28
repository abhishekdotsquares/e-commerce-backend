from pydantic import EmailStr

from app.models import User
from app.repositories import UserRepository
from app.schemas.extras.token import Token
from core.controller import BaseController
from core.database import Propagation, Transactional
from core.exceptions import BadRequestException
from core.security import JWTHandler, PasswordHandler

BLACKLIST = set()  # we can use redis for a better approach

class AuthController(BaseController[User]):
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the AuthController.

        Args:
            user_repository (UserRepository): The repository for user data operations.
        """
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    @Transactional(propagation=Propagation.REQUIRED)
    async def register(self, email: EmailStr, password: str) -> User:
        """
        Register a new user with the given email and password.

        Args:
            email (EmailStr): The email of the user to register.
            password (str): The password for the user.

        Returns:
            User: The created user instance.

        Raises:
            BadRequestException: If a user with the given email already exists.
        """
        # Check if user exists with email
        user = await self.user_repository.get_by_email(email)

        if user:
            raise BadRequestException("User already exists with this email")
        
        password = PasswordHandler.hash(password)

        return await self.user_repository.create(
            {
                "email": email,
                "password": password,
            }
        )

    async def login(self, email: EmailStr, password: str) -> Token:
        """
        Log in a user and return authentication tokens.

        Args:
            email (EmailStr): The email of the user attempting to log in.
            password (str): The password of the user.

        Returns:
            Token: An object containing the access and refresh tokens.

        Raises:
            BadRequestException: If the email is invalid or the password is incorrect.
        """
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise BadRequestException("Invalid email.")

        if not PasswordHandler.verify(user.password, password):
            raise BadRequestException("Invalid password.")

        return Token(
            access_token=JWTHandler.encode(payload={"user_id": user.id}),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
        )

    async def refresh_token(self, access_token: str, refresh_token: str) -> Token:
        """
        Refresh the user's access token using the refresh token.

        Args:
            access_token (str): The current access token.
            refresh_token (str): The refresh token.

        Returns:
            Token: An object containing the new access token and the same refresh token.

        Raises:
            BadRequestException: If the refresh token is invalid.
        """
        token = JWTHandler.decode(access_token)
        refresh_token_validate = JWTHandler.decode(refresh_token)
        if refresh_token_validate.get("sub") != "refresh_token":
            raise BadRequestException("Invalid refresh token")

        return Token(
            access_token=JWTHandler.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=refresh_token,
        )
    
    async def logout(self, access_token: str) -> None:
        """
        Logout the user by blacklisting the provided access token.

        Args:
            access_token (str): The access token to be blacklisted.
        
        Returns:
            None: Indicates successful logout.
        """
        BLACKLIST.add(access_token)
        return True
