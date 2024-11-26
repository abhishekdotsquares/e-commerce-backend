import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.enquiry.Mutation.mutation import EnquiryMutation
from app.schemas.responses.response_types import TokenType, EnquiryResponseType
from app.models.enquiry import Enquiry
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_update_enquiry_success():
    """Test updating an enquiry successfully."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {
        "db": mock_db,
        "authorization": "Bearer test_jwt_token",  # Add authorization header mock
    }

    # Input data
    enquiry_id = 1
    business_name = "Updated Business"
    email = "updated@example.com"
    password = "securepassword"
    # Mock existing enquiry
    mock_enquiry = Enquiry(id=enquiry_id, business_name="Test Business", email="test@example.com")
    mock_db.get.return_value = mock_enquiry

    # Mock commit and refresh
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Call the function
    enquiry_mutation = EnquiryMutation()
    response = await enquiry_mutation.update_enquiry(
        info=MagicMock(context=mock_context),
        id=enquiry_id,
        business_name=business_name,
        email=email,
    )

    # Assertions
    assert isinstance(response, EnquiryResponseType)
    assert response.status is True  # Updated field name
    assert response.message == "Account Updated Successfully"
    assert mock_enquiry.business_name == business_name
    assert mock_enquiry.email == email
    # assert pwd_context.verify(password, password)