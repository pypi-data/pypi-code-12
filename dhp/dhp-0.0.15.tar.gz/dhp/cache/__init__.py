'''Caching mechanisms that can be used as is or subclassed to enable
specialization.
`view the
source <https://bitbucket.org/dundeemt/dhp/src/tip/dhp/cache/__init__.py>`_
'''


class CacheMiss(Exception):
    '''Exception raised when requested key can not be found.

    Any SimpleCache operation that requires a ``key``: ``.get``, ``.put`` and
    ``.invalidate``, and the key supplied can not be found while raise a
    CacheMiss. It is a replacement for the normal KeyError but is a logically
    separate exception.

    Args:
        message (str): Human readable string describing the exception.

    Attributes:
        message (str): Human readable string describing the exception.

    Examples:

        >>> from dhp.cache import SimpleCache, CacheMiss
        >>> scache = SimpleCache()
        >>> try:
        >>>     value = scache.get(key='foo')
        >>> except CacheMiss:
        >>>     # do something meaningful like set value to a default
        >>>     # or run your expensive operation.
        >>>     pass

    '''
    pass


class CacheKeyUnhashable(Exception):
    '''Exception raised when the key given is not hashable.

    It is a replacement for the normal TypeError that would be raised in this
    situation to keep the exception logcially separated.

    Args:
        message (str): Human readable string describing the exception.

    Attributes:
        message (str): Human readable string describing the exception.
    '''
    pass


class SimpleCache(object):
    '''A simplistic cache mechanism.

    SimpleCache is an in-memory dictionary based caching mechanism. It includes
    cache stats.

    Examples:

        >>> from dhp.cache import SimpleCache
        >>> scache = SimpleCache()
        >>> scache.put(key='foo', value='bar')
        >>> scache.get(key='foo')
        'bar'

    A key can be any Python hashable object, the restrictions on value are
    the same as for a Python dict -- since that is the underlying mechansim.
    '''

    def __init__(self):
        '''initialize cache and counters'''
        self.hits = 0
        self.misses = 0
        self.invalidated = 0
        self._cache = {}

    def get(self, key):
        '''Return the cached entry indicated by key or raise CacheMiss

        Args:
            key (hashable object): The cache key to retrieve.

        Returns:
            The object associated with key.

        Raises:
            CacheMiss: If the key can not be found.
            CacheKeyUnhashable: If the key is not hashable

        '''
        try:
            value = self._cache[key]
        except KeyError:
            self.misses += 1
            raise CacheMiss('Key (%s) not found.' % key)
        except TypeError as err:
            raise CacheKeyUnhashable(str(err))

        self.hits += 1
        return value

    def put(self, key, value):
        '''Cache the value with key.

        Args:
            key (hashable object): The key to associate with the value. Keys
                are unique. The most recent ``.put`` call replaces the existing
                value, if any.
            value (object): The value to cache.

        Raises:
            CacheKeyUnhashable: if the key is not hashable.

        '''
        try:
            self._cache[key] = value
            self.misses += 1
        except TypeError as err:
            raise CacheKeyUnhashable(str(err))

    def invalidate(self, key):
        '''Invalidate an element of the cache.

        Args:
            key (hashable object): The key to remove from the cache.

        Raises:
            CacheMiss: If the key can not be found.
            CacheKeyUnhashable: If the key is not hashable.

        '''
        try:
            del self._cache[key]
            self.invalidated += 1
        except KeyError:
            raise CacheMiss('Key (%s) not found.' % key)
        except TypeError as err:
            raise CacheKeyUnhashable(str(err))

    @property
    def stats(self):
        '''(property) Returns a dictionary with cache stats.

        Returns:
            (dict): a 4 element dictionary consisting of ``cache_size``,
                ``cache_hits``, ``cache_misses`` and ``cache_invalidated``.

        '''
        return {'cache_size': len(self._cache),
                'cache_hits': self.hits,
                'cache_misses': self.misses,
                'cache_invalidated': self.invalidated}
