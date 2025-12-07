from api.api_core.schemas.error_schemas import ErrorModel


class CustomBaseException(Exception):
    @property
    def code(self) -> int:
        raise NotImplementedError

    @property
    def title(self) -> str:
        raise NotImplementedError

    @property
    def detail(self) -> str:
        raise NotImplementedError

    def to_pydantic(self) -> ErrorModel:
        return ErrorModel(code=self.code, title=self.title, detail=self.detail)


class Base400Error(CustomBaseException):
    code: int = 400
    title: str = "BadRequest"

    @property
    def detail(self) -> str:
        raise NotImplementedError


class Base403Error(CustomBaseException):
    code = 403
    title = "Access denied"


class Base404Error(CustomBaseException):
    code: int = 404
    title: str = "NotFound"

    @property
    def detail(self) -> str:
        raise NotImplementedError


class EmailAlreadyExistsError(Base400Error):
    @property
    def detail(self) -> str:
        return "User with this email already exists"


class WrongPasswordError(Base400Error):
    detail: str = "Wrong password"


class CannotDeleteOtherEvent(Base403Error):
    detail = "You do not have permission to delete this event."


class CannotUpdateOtherEvent(Base403Error):
    detail = "You do not have permission to update this event."


class UserEmailNotFoundError(Base404Error):
    detail: str = "User with such email does not exist"


class UserDoesNotExistError(Base404Error):
    detail = "User does not exist"


class EventDoesNotExistError(Base404Error):
    detail: str = "Check provided event ID. Event does not exist."


class RegistrationNotFoundError(Base404Error):
    detail: str = "Registration not found for this user and event."
