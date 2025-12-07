from typing import Any

from services.cache.cache import CacheHandler
from services.auth_services.exc import LoggedOutTokenError


class JWTCacheHandler:
    key_template_access = "user_{id}_access_tokens"
    key_template_refresh = "user_{id}_refresh_tokens"

    def __init__(self, cache: CacheHandler):
        if not isinstance(cache, CacheHandler):
            raise TypeError(
                f"Variable cache should be instance of Cache and not {type(cache)}"
            )
        self.cache = cache

    def save_to_cache_pairs(
        self, user_identifier: Any, access_token: str, refresh_token: str, ttl: int = 0
    ):
        self.cache.lpush(
            self.key_template_access.format(id=user_identifier), access_token
        )
        self.cache.lpush(
            self.key_template_refresh.format(id=user_identifier), refresh_token
        )
        self.cache.set(access_token, refresh_token)
        self.cache.set(refresh_token, access_token)
        if ttl:
            self.cache.expire(access_token, ttl)
            self.cache.expire(refresh_token, ttl)

    def update_token_pairs(
        self,
        user_identifier: Any,
        old_token: str,
        access_token: str,
        refresh_token: str,
        ttl: int = 0,
        is_access_token: bool = False,
    ):
        if is_access_token:
            old_access_token = old_token
            if (
                pos_old_acc := self.cache.lpos(
                    self.key_template_access.format(id=user_identifier),
                    old_access_token,
                )
            ) is None:
                raise LoggedOutTokenError()
            old_refresh_token = self.cache.get(old_access_token)
            pos_old_ref = self.cache.lpos(
                self.key_template_refresh.format(id=user_identifier), old_access_token
            )
        else:
            old_refresh_token = old_token
            if (
                pos_old_ref := self.cache.lpos(
                    self.key_template_refresh.format(id=user_identifier),
                    old_refresh_token,
                )
            ) is None:
                raise LoggedOutTokenError()
            old_access_token = self.cache.get(old_refresh_token)
            # remove tokens
            pos_old_acc = self.cache.lpos(
                self.key_template_access.format(id=user_identifier), old_access_token
            )
        if pos_old_acc:
            self.cache.lrem(
                self.key_template_access.format(id=user_identifier), 1, pos_old_acc
            )
        if pos_old_ref:
            self.cache.lrem(
                self.key_template_refresh.format(id=user_identifier), 1, pos_old_ref
            )
        self.cache.delete(old_refresh_token)
        self.cache.delete(old_access_token)
        self.save_to_cache_pairs(
            user_identifier=user_identifier,
            access_token=access_token,
            refresh_token=refresh_token,
            ttl=ttl,
        )

    def clear_other_sessions(self, user_identifier: Any, access_token: str):
        def remove_tokens_from_list(key: str):
            for token in self.cache.lrange(key, 0, -1):
                self.cache.delete(token)
            self.cache.delete(key)

        if (
            self.cache.lpos(
                self.key_template_access.format(id=user_identifier), access_token
            )
            is None
        ):
            raise LoggedOutTokenError()
        refresh_token = self.cache.get(access_token)
        remove_tokens_from_list(self.key_template_access.format(id=user_identifier))
        remove_tokens_from_list(self.key_template_refresh.format(id=user_identifier))

        self.save_to_cache_pairs(
            user_identifier, access_token=access_token, refresh_token=refresh_token
        )

    def verify_token(
        self, user_identifier: Any, token: str, is_access_token: bool = True
    ):
        if self.cache.get(token) is None:
            raise LoggedOutTokenError()
        if (
            is_access_token
            and self.cache.lpos(
                self.key_template_access.format(id=user_identifier), token
            )
            is None
        ):
            raise LoggedOutTokenError()
        elif (
            not is_access_token
            and self.cache.lpos(
                self.key_template_refresh.format(id=user_identifier), token
            )
            is None
        ):
            raise LoggedOutTokenError()

    def delete_pairs_tokens(self, user_identifier: Any, access_token: str):
        refresh_token = self.cache.get(access_token)
        self.cache.delete(refresh_token)
        self.cache.delete(access_token)
        self.cache.lrem(
            self.key_template_access.format(id=user_identifier), 0, access_token
        )
        self.cache.lrem(
            self.key_template_refresh.format(id=user_identifier), 0, refresh_token
        )
