import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.enquiry.Mutation.mutation import EnquiryMutation
from app.schemas.responses.response_types import TokenType, EnquiryResponseType
from core.exceptions.validation_error import ValidationError

@pytest.mark.asyncio
async def test_create_enquiry_success():
    """Test creating an enquiry successfully."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {
        "db": mock_db,
    }
    
    # Inputs
    business_name = "Test Business"
    website_link = "http://testbusiness.com"
    first_name = "John"
    last_name = "Doe"
    email = "johndoe@example.com"
    phone_number = "1234567890"

    # Mock the database query for checking existing enquiry
    async def mock_execute(*args, **kwargs):
        class MockResult:
            @property
            def raw(self):
                class MockRaw:
                    rowcount = 0  # Simulate no existing enquiries
                return MockRaw()
        return MockResult()

    mock_db.execute.side_effect = mock_execute

    # Mock commit and refresh
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    # Call the function
    enquiry_mutation = EnquiryMutation()
    response = await enquiry_mutation.createEnquiry(
        business_name=business_name,
        website_link=website_link,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        info=MagicMock(context=mock_context),
    )
    # Assertions
    assert response.status is True
    assert response.message == "Account Created Successfully.Please Log In"
