"""
Cache
"""
from collections.abc import Iterable
from logging import Logger, getLogger
from typing import Any, List, Optional

from services.cache.cache.engine_cache import EngineCache
from services.cache.cache.serializer_cache import CacheSerializer, StrCacheSerializer

DEFAULT_LOGGER = getLogger(__name__)


class CacheHandler:
    """
    Base cache class
    """

    def __init__(
        self,
        engine: EngineCache,
        serializer: CacheSerializer = StrCacheSerializer(),
        logger: Optional[Logger] = None,
        composite_key_separator: str = "_",
    ):
        """ """

        if not isinstance(engine, EngineCache):
            raise TypeError(
                f"Object engine must be of type - `{EngineCache.__name__}`, "
                f"not a `{type(engine)}`"
            )
        if not isinstance(serializer, CacheSerializer):
            raise TypeError(
                f"Object serializer must be of type - `{CacheSerializer.__name__}`, "
                f"not a `{type(serializer)}`"
            )
        self._engine = engine
        self._serializer = serializer

        if not logger:
            logger = DEFAULT_LOGGER
        self._logger = logger
        self._composite_key_separator = composite_key_separator

    def _get_key(self, key: Any) -> str:
        """ """
        if isinstance(key, Iterable) and not isinstance(key, str):
            key = f"{self._composite_key_separator}".join(list(map(str, key)))
        if not isinstance(key, str):
            key = str(key)
        return key

    def set(self, key: Any, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Set value to cache
        """
        key = self._get_key(key)
        serialized_key, serialized_value = self._serializer.serialize(key, value)
        return self._engine.set(
            key=serialized_key, value=serialized_value, ttl=ttl, **kwargs
        )

    def update_ttl(self, key: Any, ttl: int, **kwargs) -> bool:
        """
        Update ttl for concrete key
        """
        key = self._get_key(key)
        serialized_key = self._serializer.serialize_key(key)
        return self._engine.update_ttl(key=serialized_key, ttl=ttl, **kwargs)

    def get(self, key: Any, **kwargs) -> Optional[Any]:
        """
        Get data from cache
        """
        key = self._get_key(key)
        serialized_key = self._serializer.serialize_key(key)
        serialized_value = self._engine.get(serialized_key, **kwargs)
        if serialized_value:
            value = self._serializer.deserialize_value(serialized_value)
            return value
        return None

    def delete(self, key: Any, **kwargs) -> bool:
        """
        Delete key from cache
        """
        key = self._get_key(key)
        serialized_key = self._serializer.serialize_key(key)
        return self._engine.delete(serialized_key, **kwargs)

    def reset_cache(self, **kwargs):
        """
        reset all data from cache
        """
        self._engine.reset_cache(**kwargs)

    def __setitem__(self, key: Any, value: Any):
        self.set(key, value)

    def __getitem__(self, key: Any):
        return self.get(key)

    def __delitem__(self, key: Any):
        self.delete(key)

    def keys(self) -> List[str]:
        return self._engine.keys()

    def lpush(self, key: str, value: Any):
        serialized_key, serialized_value = self._serializer.serialize(key, value)
        self._engine.lpush(serialized_key, serialized_value)

    def lpos(self, key: str, value: Any) -> int:
        serialized_key, serialized_value = self._serializer.serialize(key, value)
        return self._engine.lpos(serialized_key, serialized_value)

    def lrange(self, key: str, start: int, end: int) -> List[Any]:
        serialized_key = self._serializer.serialize_key(key)
        return self._engine.lrange(serialized_key, start, end)

    def lrem(self, key: str, count: int, value: Any):
        serialized_key, serialized_value = self._serializer.serialize(key, value)
        return self._engine.lrem(serialized_key, count, serialized_value)

    def expire(self, key: Any, ttl: int, **kwargs) -> bool:
        return self.update_ttl(key, ttl, **kwargs)
