from django.conf import settings
from services.auth_services.exc import (
    IncorrectTokenError,
    IncorrectTokenTypeError,
    LoggedOutTokenError,
    TokenRequiredError,
    TTLTokenExpiredError,
    UnknownTokenValidationError,
)
from services.auth_services.security import JWTHandler


def token_authentication(token, is_access_token: bool = True):
    if not token:
        raise TokenRequiredError()
    
    try:
        JWTHandler().verify_token(token, is_access_token)
        return token
    except (
        IncorrectTokenTypeError,
        TTLTokenExpiredError,
        IncorrectTokenError,
        LoggedOutTokenError,
    ) as exc:
        raise exc
    except Exception as exc:
        msg = ""
        if settings.DEBUG:
            msg = str(exc)
        raise UnknownTokenValidationError(msg)