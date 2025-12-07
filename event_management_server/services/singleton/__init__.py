from typing import Any, Dict


class SingletonMeta(type):
    _instances = {}  # type: Dict[Any, Any]

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset_instance_force(cls):
        if cls in cls._instances:  # pragma: no cover
            del cls._instances[cls]