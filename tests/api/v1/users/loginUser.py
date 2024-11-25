import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from api.v1.users.Mutation.mutation import UserMutation, BadRequestException
from app.models.user import User
from app.schemas.responses.response_types import TokenType


# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
@patch("api.v1.users.Mutation.mutation.JWTHandler.encode", side_effect=lambda payload: "mocked_jwt_token")
async def test_login_user_success(mock_jwt_handler):
    """Test successful user login."""
    # Mock database session and context
    mock_db = AsyncMock()
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"
    password = "securepassword"

    # Mock user in database
    mock_user = User(id=1, email=email, password=pwd_context.hash(password))
    mock_db.scalar.return_value = mock_user

    # Call the function
    user_mutation = UserMutation()
    response = await user_mutation.loginUser(
        email=email,
        password=password,
        info=MagicMock(context=mock_context),
    )

    # Assertions
    assert isinstance(response, TokenType)
    assert response.access_token == "mocked_jwt_token"
    assert response.refresh_token == "mocked_jwt_token"
    assert response.token_type == "bearer"

    # Verify the `scalar` call by comparing SQL string representations
    query = select(User).where(User.email == email)
    executed_query = mock_db.scalar.call_args[0][0]  # Extract the query from call_args
    assert str(query) == str(executed_query)  # Compare SQL strings


@pytest.mark.asyncio
async def test_login_user_invalid_email():
    """Test login with an invalid email."""
    # Mock database session and context
    mock_db = AsyncMock()
    mock_context = {"db": mock_db}

    # Inputs
    email = "invalid@example.com"
    password = "securepassword"

    # Mock no user in database
    mock_db.scalar.return_value = None

    # Call the function
    user_mutation = UserMutation()
    with pytest.raises(BadRequestException) as excinfo:
        await user_mutation.loginUser(
            email=email,
            password=password,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert str(excinfo.value) == "Invalid email or password."

    # Verify the `scalar` call by comparing SQL string representations
    query = select(User).where(User.email == email)
    executed_query = mock_db.scalar.call_args[0][0]  # Extract the query from call_args
    assert str(query) == str(executed_query)  # Compare SQL strings


@pytest.mark.asyncio
async def test_login_user_invalid_password():
    """Test login with an invalid password."""
    # Mock database session and context
    mock_db = AsyncMock()
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"
    password = "wrongpassword"

    # Mock user in database
    mock_user = User(id=1, email=email, password=pwd_context.hash("securepassword"))
    mock_db.scalar.return_value = mock_user

    # Call the function
    user_mutation = UserMutation()
    with pytest.raises(BadRequestException) as excinfo:
        await user_mutation.loginUser(
            email=email,
            password=password,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert str(excinfo.value) == "Invalid email or password."

    # Verify the `scalar` call by comparing SQL string representations
    query = select(User).where(User.email == email)
    executed_query = mock_db.scalar.call_args[0][0]  # Extract the query from call_args
    assert str(query) == str(executed_query)  # Compare SQL strings


@pytest.mark.asyncio
async def test_login_user_database_error():
    """Test database error during login."""
    # Mock database session and context
    mock_db = AsyncMock()
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"
    password = "securepassword"

    # Simulate a database error
    mock_db.scalar.side_effect = SQLAlchemyError("Database error")

    # Call the function
    user_mutation = UserMutation()
    with pytest.raises(Exception) as excinfo:
        await user_mutation.loginUser(
            email=email,
            password=password,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert "Database error occurred while logging in." in str(excinfo.value)

    # Verify the `scalar` call by comparing SQL string representations
    query = select(User).where(User.email == email)
    executed_query = mock_db.scalar.call_args[0][0]  # Extract the query from call_args
    assert str(query) == str(executed_query)  # Compare SQL strings
