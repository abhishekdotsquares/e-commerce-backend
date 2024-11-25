import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select
from api.v1.users.Mutation.mutation import UserMutation
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import ANY  # Add this import at the top
from app.models.user import User
from app.schemas.responses.response_types import ForgotPasswordResponseType
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def mock_db():
    """Fixture for properly mocked AsyncSession."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.begin.return_value.__aenter__.return_value = mock_db
    return mock_db

@pytest.mark.asyncio
@patch("api.v1.users.Mutation.mutation.send_email")
async def test_forgot_password_success(mock_send_email):
    """Test successful password reset request."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.begin.return_value.__aenter__.return_value = mock_db  # Mock `async with db.begin()`
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"

    # Mock user in the database
    mock_user = User(id=1, email=email)
    mock_db.scalar.side_effect = [mock_user, None]  # First query for user, second for token creation

    # Call the mutation
    user_mutation = UserMutation()
    response = await user_mutation.forgotPassword(
        email=email,
        info=MagicMock(context=mock_context),
    )

    # Assertions
    assert isinstance(response, ForgotPasswordResponseType)
    assert response.success is True
    assert response.message == "Email sent successfully, you will receive a password reset link shortly."

    # Verify reset token was created and email was sent
    assert mock_db.add.call_count == 1
    mock_send_email.assert_called_once_with(
        to_email=email,
        subject="Password Reset Request",
        body=ANY,  # Use ANY to match any string
    )

    # Verify query to fetch user
    query_user = select(User).where(User.email == email)
    executed_user_query = mock_db.scalar.call_args_list[0][0][0]
    assert str(query_user) == str(executed_user_query)


@pytest.mark.asyncio
@patch("api.v1.users.Mutation.mutation.send_email")
async def test_forgot_password_user_not_found(mock_send_email, mock_db):
    """Test forgot password with non-existent email."""
    mock_context = {"db": mock_db}

    # Inputs
    email = "nonexistent@example.com"

    # Mock no user in the database
    mock_db.scalar.return_value = None

    # Call the mutation
    user_mutation = UserMutation()
    response = await user_mutation.forgotPassword(
        email=email,
        info=MagicMock(context=mock_context),
    )

    # Assertions
    assert isinstance(response, ForgotPasswordResponseType)
    assert response.success is False
    assert response.message == "User not found."

    # Verify no email was sent
    mock_send_email.assert_not_called()



@pytest.mark.asyncio
async def test_forgot_password_database_error():
    """Test database error during forgot password."""
    # Mock database session and context
    mock_db = AsyncMock()
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"

    # Simulate a database error
    mock_db.scalar.side_effect = SQLAlchemyError("Database error")

    # Call the mutation
    user_mutation = UserMutation()
    with pytest.raises(Exception) as excinfo:
        await user_mutation.forgotPassword(
            email=email,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert "An unexpected error occurred while processing the forgot password request." in str(excinfo.value)


@pytest.mark.asyncio
@patch("api.v1.users.Mutation.mutation.send_email")
async def test_forgot_password_email_sending_error(mock_send_email, mock_db):
    """Test email sending error during forgot password."""
    mock_context = {"db": mock_db}

    # Inputs
    email = "test@example.com"

    # Mock user in the database
    mock_user = User(id=1, email=email)
    mock_db.scalar.side_effect = [mock_user]  # Return the user for the first query

    # Simulate email sending failure
    mock_send_email.side_effect = Exception("Email sending failed")

    # Call the mutation
    user_mutation = UserMutation()
    with pytest.raises(Exception) as excinfo:
        await user_mutation.forgotPassword(
            email=email,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert "An unexpected error occurred while processing the forgot password request." in str(excinfo.value)

    # Verify email sending was attempted
    mock_send_email.assert_called_once_with(
        to_email=email,
        subject="Password Reset Request",
        body=ANY,  # Use ANY to match any string
    )
