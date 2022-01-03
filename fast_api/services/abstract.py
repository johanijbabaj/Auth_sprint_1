from abc import ABC, abstractmethod
from db.cache import MemoryCache
from db.storage import AbstractStorage


class AbstractService(ABC):

    CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

    name = None

    def __init__(self, cache: MemoryCache, storage: AbstractStorage):
        self.cache = cache
        self.storage = storage

    @abstractmethod
    def get_by_id(self):
        pass

    @abstractmethod
    def get_list(self):
        pass

    def _get_key(self, *args):
        key = (self.name, args)
        return str(key)

