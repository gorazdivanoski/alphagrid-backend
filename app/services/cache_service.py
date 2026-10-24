import time
from typing import Any, Optional

# In-memory TTL cache for temporarily storing API responses,
# with separate expiration times for stock quotes and company profiles.

class TTLCache:
    def __init__(self, ttl_seconds: int = 15):
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, value = entry
        if time.time() - timestamp > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()

# Separate caches with different TTLs - stock prices update frequently, while company profiles remain stable.
quote_cache = TTLCache(ttl_seconds=15)
profile_cache = TTLCache(ttl_seconds=3600)