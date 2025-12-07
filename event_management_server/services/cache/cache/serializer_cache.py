import codecs
import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Tuple


class CacheSerializer(ABC):
    @staticmethod
    def serialize_key(key: Any) -> Any:
        return key

    @staticmethod
    def deserialize_key(key: Any) -> Any:
        return key

    @staticmethod
    @abstractmethod
    def serialize_value(value: Any) -> Any:
        """ """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def deserialize_value(value: Any) -> Any:
        """ """
        raise NotImplementedError

    def serialize(self, key: Any, value: Any) -> Tuple[Any, Any]:
        """ """
        return self.serialize_key(key), self.serialize_value(value)

    def deserialize(self, key: Any, value: Any) -> Tuple[Any, Any]:
        """ """
        return self.deserialize_key(key), self.deserialize_value(value)


class StrCacheSerializer(CacheSerializer):
    """
    class serialize key and value to str use json lib
    """

    @staticmethod
    def serialize_key(key: Any) -> Any:
        return json.dumps(key)

    @staticmethod
    def deserialize_key(key: Any) -> Any:
        return json.loads(key)

    @staticmethod
    def serialize_value(value: Any) -> Any:
        return json.dumps(value)

    @staticmethod
    def deserialize_value(value: Any) -> Any:
        return json.loads(value)


class PickleCacheSerializer(CacheSerializer):
    @staticmethod
    def serialize_value(value: Any) -> Any:
        """
        method for serializing data
        :param: any value: data to serialize
        :return: serialized data
        """
        return codecs.encode(pickle.dumps(value), "base64").decode()

    @staticmethod
    def deserialize_value(value: Any) -> Any:
        """
        method for deserializing data
        :param: any value: data to deserialize
        :return: deserialized data
        """
        try:
            return pickle.loads(codecs.decode(value.encode(), "base64"))
        except Exception:  # noqa: E722
            return value
