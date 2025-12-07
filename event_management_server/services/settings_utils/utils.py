import os
from pydantic import BaseModel, Field
from typing import Optional


class RedisConnectSettings(BaseModel):
    host: str = Field(...)
    port: int = Field(...)
    username: Optional[str] = Field(None)
    db: Optional[int] = Field(0, gte=0, lt=20)
    password: Optional[str] = Field(None)

    def to_conn_str(self):
        auth_str = ""
        if self.password:
            auth_str = f":{self.password}@"
        return f"redis://{auth_str}{self.host}:{self.port}/{self.db}"


class SettingsConfigsHandler:
    @staticmethod
    def get_redis_config(
        redis_db_key: Optional[str] = "REDIS_CACHE_DB",
    ) -> RedisConnectSettings:
        """
        method to create redis connect config object
        :param str redis_db_key: takes optional value to set custom db key from envs
        :return RedisConnectSettings: return rabbit config object
        """
        return RedisConnectSettings(
            host=os.getenv("REDIS_HOST", default="redis"),
            port=os.getenv("REDIS_PORT", default=6379),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_HOST_PASSWORD", ""),
            db=os.getenv(redis_db_key, 2),
        )
