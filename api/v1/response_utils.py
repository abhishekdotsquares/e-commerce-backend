# response_utils.py
from typing import Optional, Type
from pydantic import BaseModel

def build_response(
    response_type: Type[BaseModel],  # This allows dynamic response types
    message: str,
    status: bool,
    data: Optional[dict] = None
):
    """
    Helper function to construct the response dynamically based on the response type.

    :param response_type: The type of the response (e.g., `CompanyResponseType`).
    :param message: Message to be included in the response.
    :param status: Status of the response (True or False).
    :param data: Optional data to include in the response.
    :return: Returns an instance of the provided `response_type`.
    """
    return response_type(
        status=status,
        message=message,
        data=data
    )
