from api.api_core.routes import EnumDetailRoutes
from api.api_core.schemas.accounts_schemas import (
    AccountSchema,
    AuthSchema,
    RegisterUserIn,
)
from api.api_core.schemas.error_schemas import BadResponse
from api.api_core.schemas.response_schema import SuccessResponse
from api.api_core.utils.exceptions import EmailAlreadyExistsError
from api.api_core.utils.response import RespModel, get_response
from apps.accounts.models import User
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from ninja import Router
from services.auth_services.auth_checker import HeaderAccessKey, HeaderRefreshKey
from services.db_handlers.accounts_handler import AccountsHandler

accounts_router = Router()


@accounts_router.post(
    path=EnumDetailRoutes.REGISTER_USER,
    summary="Register a new user",
    response={
        200: SuccessResponse,
        (400, 404): BadResponse,
    },
    auth=None,
)
def register_user(request, payload: RegisterUserIn):
    try:
        User.objects.create_user(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
        )
    except IntegrityError:
        raise EmailAlreadyExistsError()
    return SuccessResponse()


@accounts_router.post(
    EnumDetailRoutes.AUTH_LOGIN,
    summary="Auth",
    description=f"""Method for client authorization.
Returns a pair of tokens in the header:
`{HeaderRefreshKey.param_name}`, `{HeaderAccessKey.param_name}`
""",
    auth=None,
    response={200: RespModel[AccountSchema], 400: BadResponse},
)
def login_route(request: HttpRequest, response: HttpResponse, auth_data: AuthSchema):
    headers, user = AccountsHandler.user_login(data=auth_data, request=request)
    user = user.to_pydantic()
    return get_response(
        user,
        response=response,
        headers=headers,
    )
