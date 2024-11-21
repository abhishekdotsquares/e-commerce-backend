from core.exceptions.validation_error import ValidationError
from core.fastapi.middlewares.authentication import AuthBackend


async def check_authentication(authorization_header):
    check = AuthBackend()
        
    # Attempt authentication
    is_authenticated = await check.authenticate(authorization_header)

    if not is_authenticated:
        raise ValidationError("Unauthorized access")
    
    return is_authenticated