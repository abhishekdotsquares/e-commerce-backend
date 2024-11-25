import pytest
from unittest.mock import AsyncMock, MagicMock
from api.v1.users.Mutation.mutation import UserMutation
from app.models.user import User
from app.schemas.responses.response_types import UserResponseType
from core.exceptions.validation_error import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.mark.asyncio
async def test_create_user_success():
    """Test creating a user successfully."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {"db": mock_db}
    
    # Set up inputs
    email = "test@example.com"
    password = "securepassword"
    is_superuser = False

    # Mock user query to return no existing user
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    # Mock commit and refresh
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Call the function
    user_mutation = UserMutation()
    response = await user_mutation.createUser(
        email=email,
        password=password,
        is_superuser=is_superuser,
        info=MagicMock(context=mock_context),
    )

    # Assertions
    assert isinstance(response, UserResponseType)
    assert response.email == email
    assert response.is_superuser == is_superuser
    assert pwd_context.verify(password, response.password)  # Verify password is hashed correctly

@pytest.mark.asyncio
async def test_create_user_validation_error():
    """Test creating a user with missing fields."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {"db": mock_db}
    
    # Set up inputs
    email = ""
    password = ""
    is_superuser = None

    # Call the function
    user_mutation = UserMutation()
    
    with pytest.raises(ValidationError) as excinfo:
        await user_mutation.createUser(
            email=email,
            password=password,
            is_superuser=is_superuser,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert str(excinfo.value) == "All fields are required."

@pytest.mark.asyncio
async def test_create_user_existing_email():
    """Test creating a user with an existing email."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {"db": mock_db}
    
    # Set up inputs
    email = "test@example.com"
    password = "securepassword"
    is_superuser = False

    # Mock user query to return an existing user
    mock_existing_user = User(
        id=1,
        email=email,
        password="hashedpassword",
        is_superuser=is_superuser,
    )

    async def mock_execute(*args, **kwargs):
        class MockResult:
            async def scalars(self):
                return MockScalars()
        return MockResult()
    
    class MockScalars:
        async def first(self):
            return mock_existing_user  # Simulate a user found in the database

    mock_db.execute.side_effect = mock_execute

    # Call the function
    user_mutation = UserMutation()
    
    with pytest.raises(ValidationError) as excinfo:
        await user_mutation.createUser(
            email=email,
            password=password,
            is_superuser=is_superuser,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert str(excinfo.value) == f"User with email {email} already exists."

