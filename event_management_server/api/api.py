from django.http import HttpRequest
from ninja import NinjaAPI
from services.auth_services.auth_checker import HeaderAccessKey
from settings import (
    NINJA_API_DESCRIPTION,
    NINJA_API_DOCS_URL,
    NINJA_API_OPENAPI_URL,
    NINJA_API_TITLE,
    NINJA_API_VERSION,
)

from api.api_core.api_v1 import api_v1_router
from api.api_core.routes import API_PREFIX
from api.api_core.utils.exceptions import CustomBaseException

api = NinjaAPI(
    auth=HeaderAccessKey(),
    title=NINJA_API_TITLE,
    description=NINJA_API_DESCRIPTION,
    version=NINJA_API_VERSION,
    openapi_url=NINJA_API_OPENAPI_URL,
    docs_url=NINJA_API_DOCS_URL,
    urls_namespace="api",
)


@api.exception_handler(CustomBaseException)
def exception_handle_func(request: HttpRequest, exc: CustomBaseException):
    resp = exc.to_pydantic()
    return api.create_response(
        request,
        resp,
        status=resp.code,
    )


api.add_router(prefix=API_PREFIX, router=api_v1_router)
