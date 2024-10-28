from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int  # User ID
    email: str  # User email address

    class Config:
        """Configuration for the Pydantic model."""
        
        from_attributes = True  # Allows the model to populate from attributes
