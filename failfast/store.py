from abc import ABCMeta, abstractmethod
from typing import Dict, Callable, Any
import time


class Store(metaclass=ABCMeta):
    """
    A Store is used to persist the status of broken backends during a period
    of time.
    """

    @abstractmethod
    def set_broken(self, key: str, ttl_seconds: int) -> None:
        """Mark the backend identified by 'key' as currently failing, expiring after 'ttl_seconds' seconds"""

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset the backend identified by 'key' so it is marked as working again"""

    @abstractmethod
    def is_broken(self, key: str) -> bool:
        """Check if the backend specified by 'key' is currently broken"""


class InProcessStore(Store):
    """
    Pure in-process implementation of a Store. Only recommended for single process
    applications or development environments
    """

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._data: Dict[str, float] = {}
        self._clock = clock

    def set_broken(self, key: str, ttl_seconds: int) -> None:
        self._data[key] = self._clock() + ttl_seconds

    def reset(self, key: str) -> None:
        self._data.pop(key, None)

    def is_broken(self, key: str) -> bool:
        return self._data.pop(key, 0) > self._clock()


class DjangoCacheStore(Store):
    """
    A Store implementation based on a django cache object.
    *Important* : Make sure your django cache is using redis/memcached or
    any other shared store if using this in a multi process or hosts environment
    """

    def __init__(self, cache: Any) -> None:
        self._cache = cache

    def set_broken(self, key: str, ttl_seconds: int) -> None:
        self._cache.set(key, True, ttl_seconds)

    def reset(self, key: str) -> None:
        self._cache.delete(key)

    def is_broken(self, key: str) -> bool:
        return bool(self._cache.get(key, False))
