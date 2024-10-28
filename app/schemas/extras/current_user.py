from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    """
    Pydantic model representing the currently authenticated user.

    Attributes:
        id (int): The unique identifier for the user.
    """
    id: int = Field(None, description="User ID")

    class Config:
        """
        Pydantic model configuration.
        
        Attributes:
            validate_assignment (bool): Enables validation on assignment of attributes.
        """
        validate_assignment = True
