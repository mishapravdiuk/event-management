from logging import Logger, getLogger
from typing import Any, List, Optional

import redis
from pydantic import BaseModel

from .cache import EngineCache

DEFAULT_LOGGER = getLogger(__name__)


class RedisConnectSettings(BaseModel):
    host: str = "redis"
    port: int = 6379
    username: Optional[str] = None
    password: Optional[str] = None
    db: Optional[int] = 0


class RedisCacheEngine(EngineCache):
    """
    cache core implementation for redis
    """

    def __init__(
        self,
        config: RedisConnectSettings,
        logger: Optional[Logger] = None,
    ):
        """
        Init redis cache engine
        parameter when initializing an object with a higher
         priority than the parameter from the config
        config structure
        redis:
            redis_host: ""
            redis_port: Optional
            redis_password: Optional
            redis_default_db: Optional
            redis_db: 3
        """
        if not logger:
            logger = DEFAULT_LOGGER

        self._set_logger(logger)

        self._config = config
        self._connect()

    def __del__(self):
        self._disconnect()

    def _connect(self):
        self.connect = redis.Redis(
            host=self._config.host,
            port=self._config.port,
            db=self._config.db,
            password=self._config.password,
            charset="utf-8",
            decode_responses=True,
        )
        self._logger.info("RedisCacheEngine was connection to redis")

    def _disconnect(self):
        try:
            self.connect.close()
        except:  # noqa
            self._logger.warning(
                "RedisCacheEngineError: in time _disconnect", exc_info=True
            )

        self._logger.info("RedisCacheEngine was disconnection from redis")

    def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        res = self.connect.set(key, value)
        if ttl and res:
            self.update_ttl(key=key, ttl=ttl)
        return res

    def update_ttl(self, key: str, ttl: int, **kwargs) -> bool:
        return self.connect.expire(name=key, time=ttl)

    def get(self, key: str, **kwargs) -> Optional[Any]:
        resp = None
        try:
            resp = self.connect.get(key)
        except redis.exceptions.ResponseError:
            pass
        except Exception as exc:
            raise exc
        return resp

    def delete(self, key: str, **kwargs) -> bool:
        return bool(self.connect.delete(key))

    def reset_cache(self, **kwargs):
        self.connect.flushdb()

    def expire(self, key: str, ttl: int):
        self.update_ttl(key=key, ttl=ttl)

    def keys(self) -> List[str]:
        return self.connect.keys()

    def lpush(self, key: str, value: Any):
        self.connect.lpush(key, value)

    def lpos(self, key: str, value: Any) -> int:
        return self.connect.lpos(key, value)

    def lrange(self, key: str, start: int, end: int) -> List[Any]:
        return self.connect.lrange(name=key, start=start, end=end)

    def lrem(self, key: str, count: int, val: Any):
        self.connect.lrem(name=key, count=count, value=val)
