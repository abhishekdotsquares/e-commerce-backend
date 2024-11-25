import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enquiry import Enquiry
from core.exceptions.validation_error import ValidationError
from app.schemas.responses.response_types import CompanyResponseType


from api.v1.enquiry.Mutation.mutation import EnquiryMutation  # Import EnquiryMutation here


# @pytest.mark.asyncio
# async def test_approve_enquiry_success():
#     """Test approving an enquiry successfully."""
#     # Mock database session and context
#     mock_db = AsyncMock(spec=AsyncSession)
#     mock_context = {"db": mock_db}

#     # Input data
#     enquiry_id = 1

#     # Mock existing enquiry
#     mock_enquiry = Enquiry(
#         id=enquiry_id,
#         is_approved=False,
#         business_name="Test Business",
#         email="test@example.com",
#         phone_number="1234567890",
#         first_name="John",
#         last_name="Doe",
#         website_link="https://example.com",
#     )
#     mock_db.get.return_value = mock_enquiry

#     # Mock createCompany function for successful company creation
#     async def mock_create_company(db, business_name, website_link, first_name, last_name, email, phone_number):
#         return CompanyResponseType(
#             id=1,
#             business_name=business_name,
#             website_link=website_link,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             phone_number=phone_number,
#         )

#     # Patch the createCompany function to use the mock
#     with patch('api.v1.companies.utils.createCompany.createCompany', mock_create_company):
#         # Mock commit and refresh methods
#         mock_db.commit.return_value = None
#         mock_db.refresh.return_value = None

#         # Call the mutation
#         enquiry_mutation = EnquiryMutation()
#         response = await enquiry_mutation.approveEnquiry(
#             id=enquiry_id,
#             info=MagicMock(context=mock_context),
#         )

#         # Assertions
#         assert response == f"Enquiry with ID {enquiry_id} approved and company created successfully."
#         assert mock_enquiry.is_approved is True
#         mock_db.commit.assert_called()
#         mock_db.refresh.assert_called_once_with(mock_enquiry)




@pytest.mark.asyncio
async def test_approve_enquiry_already_approved():
    """Test approving an already approved enquiry."""
    # Mock database session and context
    mock_db = AsyncMock(spec=AsyncSession)
    mock_context = {"db": mock_db}

    # Input data
    enquiry_id = 1

    # Mock existing enquiry with is_approved = True
    mock_enquiry = Enquiry(
        id=enquiry_id,
        is_approved=True,
        business_name="Test Business",
        email="test@example.com",
        phone_number="1234567890",
        first_name="John",
        last_name="Doe",
        website_link="https://example.com"
    )
    mock_db.get.return_value = mock_enquiry

    # Call the mutation
    enquiry_mutation = EnquiryMutation()
    
    with pytest.raises(ValidationError) as excinfo:
        await enquiry_mutation.approveEnquiry(
            id=enquiry_id,
            info=MagicMock(context=mock_context),
        )

    # Assertions
    assert str(excinfo.value) == f"Enquiry with ID {enquiry_id} is already approved."
    mock_db.commit.assert_not_called()



