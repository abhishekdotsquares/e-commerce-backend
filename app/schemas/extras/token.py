from pydantic import BaseModel

class Token(BaseModel):
    """
    Pydantic model representing an authentication token.

    Attributes:
        access_token (str): The token used for accessing protected resources.
        refresh_token (str): The token used to obtain a new access token when the current one expires.
    """
    access_token: str
    refresh_token: str
