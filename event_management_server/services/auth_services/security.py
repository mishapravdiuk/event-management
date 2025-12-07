import uuid
import datetime
import jwt
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from services.singleton import SingletonMeta
from services.auth_services.jwt_cache_handler import JWTCacheHandler
from services.cache.cache import CacheHandler
from services.auth_services.exc import (
    IncorrectPathInEncodedDataError,
    IncorrectTokenError,
    IncorrectTokenTypeError,
    TTLTokenExpiredError,
)


DEFAULT_TTL_ACCESS_TOKEN = 600
DEFAULT_TTL_REFRESH_TOKEN = 1209600


class JWTHandlerConfig(BaseModel):
    is_use_cache: bool = Field(True, description="Is use cache for save tokens")
    ttl_access_token: int = Field(
        DEFAULT_TTL_ACCESS_TOKEN, description="How to long live access token"
    )
    ttl_refresh_token: int = Field(
        DEFAULT_TTL_REFRESH_TOKEN, description="How to long live refresh token"
    )
    secret: str = Field(str(uuid.uuid4()), description="Secret jwt tokens")
    algorithm: str = Field("HS256", description="Algorithm encoding jwt tokens")
    user_identifier_in_user_data: str = Field(
        "id",
        description="Path in dictionary data to user identifier by keys."
        " Deep separate by keys. "
        "for dictionary: {'data':{'user':{'id': int, `some data`: `some value`}}}"
        "value: `data.user.id` ",
    )


class JWTHandler(metaclass=SingletonMeta):
    """
    JWTHandler class for checking the validity of sessions
    """

    _access_token_type: str = "access_token"
    _refresh_token_type: str = "refresh_token"
    _cache_handler: JWTCacheHandler = None
    _is_use_cache: bool

    def __init__(
        self,
        config: Optional[JWTHandlerConfig] = None,
        cache: Optional[CacheHandler] = None,
    ):
        self._config = config
        self._is_use_cache = False

        if cache:
            self._is_use_cache = True
            self._cache_handler = JWTCacheHandler(cache)

    def _encode_token(
        self,
        data: Dict[str, Any],
        token_type: str,
        exp: datetime.datetime,
        headers: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate jwt token
        :param data: serialized user data
        :type data: Dict[str, Any]
        :param token_type: one of token type
        :type token_type: str
        :param exp: time expired token
        :type exp: datetime.datetime
        :param headers: headers jwt token
        :type headers: Optional[Dict[str, Any]]
        :return: jwt token
        :rtype: str
        """
        payload = {
            "type": token_type,
            "exp": exp,
            "sub": str(data[self._config.user_identifier_in_user_data]),
            "user_data": data,
            "uuid": str(uuid.uuid4()),
        }
        
        return jwt.encode(
            payload=payload,
            key=self._config.secret,
            algorithm=self._config.algorithm,
            headers=headers,
        )

    def _decode_token(self, token: str, verify: bool = True) -> Dict[str, Any]:
        """
        Decode information from token
        """
        return jwt.decode(
            token,
            key=self._config.secret,
            algorithms=[
                self._config.algorithm,
            ],
            verify=verify,
        )

    def get_subject(self, token: str) -> Dict[str, Any]:
        return self._decode_token(token, verify=False)["sub"]

    @staticmethod
    def _get_expired_datetime(ttl_token: int) -> datetime.datetime:
        """
        Get expired time for token
        :param ttl_token: ttl token in seconds
        :type ttl_token: int
        :return: expired datetime
        :rtype: datetime.datetime
        """
        return datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=ttl_token
        )

    def _get_access_token(
        self, subject_user, headers: Optional[Dict[str, Any]] = None, ttl: int = None
    ) -> str:
        return self._encode_token(
            subject_user,
            self._access_token_type,
            exp=self._get_expired_datetime(ttl or self._config.ttl_access_token),
            headers=headers,
        )

    def _get_refresh_token(
        self, subject_user, headers: Optional[Dict[str, Any]] = None, ttl: int = None
    ) -> str:
        return self._encode_token(
            subject_user,
            self._refresh_token_type,
            exp=self._get_expired_datetime(ttl or self._config.ttl_refresh_token),
            headers=headers,
        )

    def get_user_identifier(
        self, *, subject_user: Dict[str, Any] = None, token: str = None
    ) -> Any:
        """
        Extract user identifier from provided data
        :param subject_user: provided user data
        :type subject_user: dict
        :param token:
        :type token: str
        :return: user identifier
        :exception UserDataForGenerateToken: if provided incorrect
         USER_IDENTIFIER_IN_USER_DATA in settings
        :exception AttributeError: if not provided data for execution
        """
        if token:
            # subject_user = self.get_subject(token)
            payload = self._decode_token(token, verify=False)
            subject_user = payload.get("user_data")
        if not subject_user:
            raise AttributeError("Should be provided `token` or `subject_user`")
        deep_path = self._config.user_identifier_in_user_data.split(".")
        for path in deep_path:
            if (subject_user := subject_user.get(path, None)) is None:
                raise IncorrectPathInEncodedDataError()
        return subject_user

    def generate_token_pairs(
        self,
        subject_user: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        ttl_access: int = None,
        ttl_refresh: int = None,
    ) -> Tuple[str, str]:
        """Generate pair tokens

        Args:
            subject_user (Dict[str, Any]): The user data
            headers (Optional[Dict[str, Any]]): additional headers
            ttl_access (int): ttl access token
            ttl_refresh (int): ttl refresh token
        Returns:
            Tuple[str, str]: pair tokens
        """
        access_token = self._get_access_token(subject_user, headers, ttl=ttl_access)
        refresh_token = self._get_refresh_token(subject_user, headers, ttl=ttl_refresh)
        if self._is_use_cache and self._cache_handler:
            user_identifier = self.get_user_identifier(subject_user=subject_user)
            self._cache_handler.save_to_cache_pairs(
                user_identifier,
                access_token,
                refresh_token,
                ttl=self._config.ttl_refresh_token,
            )
        return access_token, refresh_token

    def update_token_pairs(
        self,
        subject_user: Dict[str, Any],
        old_token: str,
        headers: Optional[Dict[str, Any]] = None,
        is_access_token: bool = False,
    ):
        self.verify_token(old_token, is_access_token=is_access_token)
        access_token = self._get_access_token(subject_user, headers)
        refresh_token = self._get_refresh_token(subject_user, headers)

        if self._is_use_cache and self._cache_handler:
            user_identifier = self.get_user_identifier(subject_user=subject_user)

            self._cache_handler.update_token_pairs(
                user_identifier=user_identifier,
                old_token=old_token,
                access_token=access_token,
                refresh_token=refresh_token,
                ttl=self._config.ttl_refresh_token,
                is_access_token=is_access_token,
            )
        return access_token, refresh_token

    def verify_token(self, token: str, is_access_token: bool = True):
        """
        Method for verify token
        :param token:
        :param is_access_token:
        :exception:
        """
        try:
            data = self._decode_token(token)
            token_type = self._refresh_token_type
            if is_access_token:
                token_type = self._access_token_type
            if data["type"] != token_type:
                raise IncorrectTokenTypeError()
            if self._is_use_cache and self._cache_handler:
                user_identifier = self.get_user_identifier(token=token)
                self._cache_handler.verify_token(
                    user_identifier=user_identifier,
                    token=token,
                    is_access_token=is_access_token,
                )
        except (jwt.InvalidSignatureError, jwt.DecodeError):
            raise IncorrectTokenError()
        except jwt.ExpiredSignatureError:
            raise TTLTokenExpiredError()

    def logout_other_users(self, access_token: str):
        if self._is_use_cache and self._cache_handler:
            user_identifier = self.get_user_identifier(token=access_token)
            self._cache_handler.clear_other_sessions(
                user_identifier=user_identifier, access_token=access_token
            )

    def logout_user(self, access_token: str):
        if self._is_use_cache and self._cache_handler:
            user_identifier = self.get_user_identifier(token=access_token)
            self._cache_handler.delete_pairs_tokens(
                user_identifier=user_identifier, access_token=access_token
            )
