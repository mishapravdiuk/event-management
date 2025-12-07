import os

from services.auth_services.security import JWTHandler, JWTHandlerConfig
from services.cache.cache import CacheHandler, StrCacheSerializer
from services.cache.redis_cache import RedisCacheEngine
from services.settings_utils.utils import SettingsConfigsHandler

JWTHandler.reset_instance_force()

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
JWT_TTL_ACCESS = os.environ.get("JWT_TTL_ACCESS")
JWT_TTL_REFRESH = os.environ.get("JWT_TTL_REFRESH")
USER_IDENTIFIER_IN_USER_DATA = "id"


JWT_HANDLER = JWTHandler(
    cache=CacheHandler(
        engine=RedisCacheEngine(
            config=SettingsConfigsHandler.get_redis_config(redis_db_key="REDIS_AUTH_DB")
        ),
        serializer=StrCacheSerializer(),
    ),
    config=JWTHandlerConfig(
        is_use_cache=True,
        ttl_access_token=JWT_TTL_ACCESS,
        ttl_refresh_token=JWT_TTL_REFRESH,
        secret=JWT_SECRET,
        algorithm=JWT_ALGORITHM,
        user_identifier_in_user_data=USER_IDENTIFIER_IN_USER_DATA,
    ),
)
