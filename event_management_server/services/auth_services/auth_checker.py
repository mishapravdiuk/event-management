from ninja.security import APIKeyHeader
from services.auth_services.utils import token_authentication


class AuthCheck:
    param_name = "ACCESS-TOKEN"

    def authenticate(self, request, token, is_access_token: bool = True):
        return token_authentication(token=token, is_access_token=is_access_token)


class HeaderAccessKey(AuthCheck, APIKeyHeader):
    pass


class HeaderRefreshKey(AuthCheck, APIKeyHeader):
    param_name = "REFRESH-TOKEN"

    def authenticate(self, request, token, is_access_token: bool = True):
        return super(HeaderRefreshKey, self).authenticate(
            request=request, token=token, is_access_token=False
        )