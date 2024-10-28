from app.models import User
from app.repositories import UserRepository
from core.controller import BaseController


class UserController(BaseController[User]):
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the UserController.

        Args:
            user_repository (UserRepository): The repository for user data operations.
        """
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User: The user instance corresponding to the provided email.

        Raises:
            ValueError: If no user is found with the provided email.
        """
        return await self.user_repository.get_by_email(email)

