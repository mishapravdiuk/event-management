"""
Module with abstract class for engines
"""
import warnings
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, List, Optional


class EngineCache(ABC):
    """
    Base class for engines
    """

    _logger = Logger(__name__)

    @abstractmethod
    def set(self, key: Any, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Set data to cache
        """
        raise NotImplementedError

    def update_ttl(self, key: Any, ttl: int, **kwargs) -> bool:
        """
        Update ttl for concrete key
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Any, **kwargs) -> Optional[Any]:
        """
        Get data from cache
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: Any, **kwargs) -> bool:
        """
        Delete data from cache
        """
        raise NotImplementedError

    @abstractmethod
    def reset_cache(self, **kwargs) -> bool:
        """
        Reset all keys
        """
        raise NotImplementedError

    @abstractmethod
    def _connect(self):
        """
        Connect to storage
        """
        raise NotImplementedError

    @abstractmethod
    def _disconnect(self):
        """
        disconnect from storage
        """
        raise NotImplementedError

    def _set_logger(self, logger: Logger) -> None:
        """
        save logger
        """
        if not isinstance(logger, Logger):
            warnings.warn(
                "Logger is not installed because the wrong type."
                " Uses the default logger",
                ResourceWarning,
            )
            return
        self._logger = logger

    @abstractmethod
    def expire(self, key: str, ttl: int):
        raise NotImplementedError

    @abstractmethod
    def keys(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def lpush(self, key: str, value: Any):
        raise NotImplementedError

    @abstractmethod
    def lpos(self, key: str, value: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def lrange(self, key: str, start: int, end: int) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def lrem(self, key: str, count: int, val: Any):
        raise NotImplementedError
