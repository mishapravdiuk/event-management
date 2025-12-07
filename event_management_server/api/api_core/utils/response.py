from enum import Enum
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar

from api.api_core.schemas.error_schemas import ErrorModel
from django.http import HttpResponse
from pydantic import BaseModel
from pydantic.generics import GenericModel

SubPydanticBaseModel = TypeVar("SubPydanticBaseModel", bound=BaseModel)


class ResponseStatusesEnum(Enum):
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"


class RespModel(GenericModel, Generic[SubPydanticBaseModel]):
    status: str
    data: SubPydanticBaseModel


def get_response(
    data: BaseModel,
    response: HttpResponse = None,
    headers: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    cookies: Optional[Dict[str, str]] = None,
    status_message: Optional[ResponseStatusesEnum] = None,
) -> Tuple[int, Dict[str, Any]]:
    if isinstance(data, ErrorModel):
        content = dict(status=ResponseStatusesEnum.ERROR.value, data=data.dict())
        status_code = data.code
    else:
        content = dict(status=ResponseStatusesEnum.SUCCESS.value, data=data.dict())
    if headers:
        for header_key, header_value in headers.items():
            response[header_key] = header_value
    if cookies:
        for cookie_name, cookie_value in cookies.items():
            response.set_cookie(key=cookie_name, value=cookie_value)
    if status_message:
        content["status"] = status_message.value
    return status_code, content
