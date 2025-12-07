from typing import Optional, Tuple

from api.api_core.schemas.accounts_schemas import AuthSchema
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from api.api_core.utils.exceptions import UserEmailNotFoundError, WrongPasswordError
from api.api_core.schemas.accounts_schemas import AccountResponseSchema
from services.auth_services.auth_checker import HeaderAccessKey, HeaderRefreshKey
from settings import JWT_HANDLER
from api.api_core.utils.exceptions import UserDoesNotExistError

User = get_user_model()


class AccountsHandler:
    @staticmethod
    def check_user(email: str, user_id: Optional[int] = None) -> bool:
        user = User.objects.filter(email=email)
        if user_id is not None:
            user = user.exclude(id=user_id)
        return user.exists()

    @staticmethod
    def generate_jwt_headers(user_model: AccountResponseSchema) -> dict:
        headers = dict()
        access_token, refresh_token = JWT_HANDLER.generate_token_pairs(
            user_model.to_dict()
        )
        headers[HeaderAccessKey.param_name] = access_token
        headers[HeaderRefreshKey.param_name] = refresh_token
        return headers

    @staticmethod
    def user_login(
        data: AuthSchema, request: HttpRequest
    ) -> Tuple[dict, User]: 
        if not AccountsHandler.check_user(data.email):
            raise UserEmailNotFoundError()
        user = User.objects.get(email=data.email)

        if not user.check_password(data.password.get_secret_value()):
            raise WrongPasswordError()

        user_model = user.to_pydantic()
        headers = AccountsHandler.generate_jwt_headers(user_model)
        result = User.objects.filter(email=user.email)
        return headers, result.first()
    
    @staticmethod
    def get_user_by_id(request: HttpRequest) -> User:
        user_id = JWT_HANDLER.get_user_identifier(token=request.auth)
        users = User.objects.filter(id=user_id)
        if users.exists():
            user = users.first()
            return user
            
        raise UserDoesNotExistError()
