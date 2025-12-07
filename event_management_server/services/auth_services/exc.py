from typing import Optional

from api.api_core.utils.exceptions import CustomBaseException



class AuthError(CustomBaseException):
    code = 403
    title = "Access token error"

    @property
    def detail(self) -> str:
        raise NotImplementedError


class LoggedOutTokenError(AuthError):
    detail = "Your session has been forcibly terminated."


class TokenRequiredError(AuthError):
    detail = "The token is required to fulfill the request"


class TTLTokenExpiredError(AuthError):
    detail = "The token has expired. Please refresh pairs or log in again."


class IncorrectTokenError(AuthError):
    detail = "Wrong token."


class IncorrectTokenTypeError(AuthError):
    detail = "Another type of token is expected"


class UnknownTokenValidationError(AuthError):
    detail = "Unknown token validation error. Contact developers for details. "

    def __init__(self, message: str = ""):
        self.detail += message


class IncorrectPathInEncodedDataError(AuthError):
    code = 409
    title = "Server error"
    detail = "Issues with token generation. Incorrect user ID."


class UnknownServerError(AuthError):
    code = 500
    title = "Server error"
    detail = "Unknown Server Error."

    def __init__(self, message: Optional[str] = None):
        if message:
            self.detail += message


class SecretTokenRequired(CustomBaseException):
    code = 403
    title = "Access Denied"
    detail = "Token is required"


class InvalidSecretToken(CustomBaseException):
    code = 403
    title = "Access Denied"
    detail = "Invalid token"