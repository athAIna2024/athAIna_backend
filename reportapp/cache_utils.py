import hashlib
from django.core.cache import cache
from typing import Any, Optional


def generate_cache_key(user_id: int, studyset_id: int, key_prefix: str, subkey: str) -> str:
    hashed_date = hashlib.md5(f"{subkey}".encode()).hexdigest()
    key = f"{key_prefix}_{user_id}_{studyset_id}_{hashed_date}"
    return key


def set_cache(user_id: int, studyset_id: int, key_prefix: str, subkey: str, value: Any, minutesExpiration: int) -> None:
    key = generate_cache_key(user_id, studyset_id, key_prefix, subkey)
    timeout = 60 * minutesExpiration
    cache.set(key, value, timeout)


def get_cache(user_id: int, studyset_id: int, key_prefix: str, subkey: str) -> Optional[Any]:
    key = generate_cache_key(user_id, studyset_id, key_prefix, subkey)
    return cache.get(key)


def delete_cache_by_pattern(user_id: int, studyset_id: int, key_prefix: str) -> None:
    key_pattern = f"{key_prefix}_{user_id}_{studyset_id}*"
    cache.delete_pattern(key_pattern)
