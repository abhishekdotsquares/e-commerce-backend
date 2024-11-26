import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.enquiry.Mutation.mutation import EnquiryMutation
from app.schemas.responses.response_types import EnquiryResponseType
from app.models.enquiry import Enquiry

@pytest.mark.asyncio
async def test_delete_enquiry_success():
    """Test deleting an enquiry successfully."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {
        "db": mock_db,
        "authorization": "Bearer test_jwt_token",  # Add authorization header mock
    }

    # Input data
    enquiry_id = 1

    # Mock existing enquiry
    mock_enquiry = Enquiry(id=enquiry_id)
    mock_db.get.return_value = mock_enquiry

    # Mock commit
    mock_db.commit.return_value = None

    # Call the function
    enquiry_mutation = EnquiryMutation()
    response = await enquiry_mutation.delete_enquiry(
        id=enquiry_id,
        info=MagicMock(context=mock_context),
    )

    # Assertions
    assert response == f"Enquiry with ID {enquiry_id} has been successfully deleted."
    mock_db.delete.assert_called_once_with(mock_enquiry)
