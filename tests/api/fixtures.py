from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime, timedelta, timezone

from app.models.passwordResetToken import PasswordResetToken

@pytest.fixture
def mock_db():
    """Fixture for properly mocked AsyncSession."""
    mock_db = AsyncMock()
    mock_db.begin.return_value.__aenter__.return_value = mock_db
    return mock_db

@pytest.fixture
def valid_reset_token():
    """Fixture for a valid password reset token."""
    return PasswordResetToken(
        token="valid-token",
        user_id=1,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
