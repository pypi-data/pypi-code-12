from .adapter.abstract import NotSupported
from .adapter.inmemory import InMemory
from .mixin            import DictionaryAccess

class Storage(DictionaryAccess):
    def __init__(self, driver = None):
        self.driver = driver or InMemory()

    def get(self, key):
        return self.driver.get(key)

    def set(self, key, value, ttl = None):
        self.driver.set(key, value, ttl)

    def remove(self, key):
        self.driver.remove(key)

    def find(self, *args, **kwargs):
        try:
            return self.driver.find(*args, **kwargs)
        except NotSupported as e:
            return []
