# import pytest
# from unittest.mock import AsyncMock, MagicMock, patch
# from datetime import datetime, timezone, timedelta
# from api.v1.users.Mutation.mutation import UserMutation
# from app.models.passwordResetToken import PasswordResetToken
# from app.models.user import User


# @pytest.mark.asyncio
# @patch("api.v1.users.Mutation.mutation.pwd_context")
# async def test_reset_password_success(mock_pwd_context):
#     """Test resetting password successfully."""
#     # Mock database and context
#     mock_db = AsyncMock()
#     mock_context = {"db": mock_db}

#     # Mock a valid reset token and user
#     valid_reset_token = PasswordResetToken(
#         token="valid-token",
#         expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
#         user_id=1
#     )
#     mock_user = User(id=1, email="test@example.com", password="oldpassword")

#     # Configure the mock db
#     mock_db.begin.return_value = AsyncMock()  # Proper async context manager
#     mock_db.scalar.side_effect = [valid_reset_token]  # Simulate query returning a valid reset token
#     mock_db.get.return_value = mock_user  # Simulate fetching the user by ID
#     mock_pwd_context.hash.return_value = "hashed-newpassword"  # Mock password hashing

#     # Call the mutation
#     user_mutation = UserMutation()
#     response = await user_mutation.resetPassword(
#         token="valid-token",
#         new_password="newpassword",
#         info=MagicMock(context=mock_context),
#     )

#     # Assertions
#     assert response.success is True
#     assert response.message == "Password has been reset successfully. You can now log in with your new password."
#     mock_db.commit.assert_called_once()  # Ensure changes are committed


# @pytest.mark.asyncio
# async def test_reset_password_invalid_token():
#     """Test resetting password with invalid or expired token."""
#     # Mock database and context
#     mock_db = AsyncMock()
#     mock_context = {"db": mock_db}

#     # Simulate no reset token found
#     mock_db.begin.return_value = AsyncMock()  # Proper async context manager
#     mock_db.scalar.return_value = None  # Simulate query returning no results

#     # Call the mutation
#     user_mutation = UserMutation()
#     response = await user_mutation.resetPassword(
#         token="invalid-token",
#         new_password="newpassword",
#         info=MagicMock(context=mock_context),
#     )

#     # Assertions
#     assert response.success is False
#     assert response.message == "Invalid or expired token."


# @pytest.mark.asyncio
# async def test_reset_password_expired_token():
#     """Test resetting password with an expired token."""
#     # Mock database and context
#     mock_db = AsyncMock()
#     mock_context = {"db": mock_db}

#     # Mock an expired reset token
#     expired_reset_token = PasswordResetToken(
#         token="valid-token",
#         expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Token is expired
#         user_id=1
#     )
#     mock_db.begin.return_value = AsyncMock()  # Proper async context manager
#     mock_db.scalar.side_effect = [expired_reset_token]

#     # Call the mutation
#     user_mutation = UserMutation()
#     response = await user_mutation.resetPassword(
#         token="valid-token",
#         new_password="newpassword",
#         info=MagicMock(context=mock_context),
#     )

#     # Assertions
#     assert response.success is False
#     assert response.message == "The reset token has expired. Please request a new one."


# @pytest.mark.asyncio
# async def test_reset_password_user_not_found():
#     """Test resetting password with no associated user."""
#     # Mock database and context
#     mock_db = AsyncMock()
#     mock_context = {"db": mock_db}

#     # Mock a valid reset token
#     valid_reset_token = PasswordResetToken(
#         token="valid-token",
#         expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
#         user_id=1
#     )
#     mock_db.begin.return_value = AsyncMock()  # Proper async context manager
#     mock_db.scalar.side_effect = [valid_reset_token]
#     mock_db.get.return_value = None  # Simulate no user found

#     # Call the mutation
#     user_mutation = UserMutation()
#     response = await user_mutation.resetPassword(
#         token="valid-token",
#         new_password="newpassword",
#         info=MagicMock(context=mock_context),
#     )

#     # Assertions
#     assert response.success is False
#     assert response.message == "User associated with the reset token not found."
