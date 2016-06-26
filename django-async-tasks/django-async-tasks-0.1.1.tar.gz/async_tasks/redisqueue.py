import pickle, redis, uuid, hashlib
from time import time as _time
from time import sleep as _sleep
from Queue import Full, Empty


RedisQueuePool = None


class RedisQueue:
    """ Simple Queue with Redis Backend"""
    
    def __init__(self, maxsize=0, queue_name=None, **redis_kwargs):
        """Redis connection parameters are:
        host='localhost', port=6379, db=0
        OR
        cache_setting_name='default'
        """
        
        global RedisQueuePool
        
        if queue_name is None:
            queue_name = uuid.uuid4().hex
        
        if RedisQueuePool is None:
            #if hasattr(redis_kwargs, 'cache_setting_name'):
            #    try:
            r = self.get_redis_connection(redis_kwargs.get('cache_setting_name'))
            RedisQueuePool = r.connection_pool
            #    except NotImplementedError:
            #        RedisQueuePool = redis.ConnectionPool(**redis_kwargs)
            #else:
            #    RedisQueuePool = redis.ConnectionPool(**redis_kwargs)

        self.__db = redis.StrictRedis(connection_pool=RedisQueuePool)
        self.key = 'rq:' + queue_name
        self.key_process = self.key + ':process'
        self.maxsize = maxsize
        self.exists_cache = None

    def get_redis_connection(self, alias='default', write=True):

        try:
            from django.core.cache import caches
        except ImportError:
            from django.core.cache import get_cache
        else:
            def get_cache(alias):
                return caches[alias]

        cache = get_cache(alias)

        if not hasattr(cache, "master_client"):
            raise NotImplementedError

        return cache.master_client
        
    def __serialize(self, item):
        """Serialize for item objects"""
    
        return pickle.dumps(item)
    
    def __unserialize(self, item):
        """Unserialize for item objects"""

        return pickle.loads(item)    

    def qsize(self):
        """Return the approximate size of the queue."""
        
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        
        return self.qsize() == 0

    def full(self):
        """Return True if the queue is full (> maxsize), False otherwise."""
        
        return self.maxsize>0 and self.qsize() >= self.maxsize

    def put(self, item, block=True, timeout=None): 
        """Put item into the queue"""

        if self.maxsize > 0:
            if not block:
                if self.qsize() >= self.maxsize:
                    raise Full('Redis queue is full')
            elif timeout is None:
                while self.qsize() >= self.maxsize:
                    _sleep(0.1)
            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = _time() + timeout
                while self.qsize() >= self.maxsize:
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Full('Redis queue is full')
                    _sleep(0.1)
        
        if type(item) is not list:
            item = [item, ]
        elif len(item)<1:
            return False
            
        pipe = self.__db.pipeline()   
        for i in item:
            i = self.__serialize(i)
            pipe.lpush(self.key, i)    
        pipe.execute()      

    def put_nowait(self, item):
        """Equivalent to put(item, False)."""
        
        return self.put(item, block=False)

    def get(self, block=True, timeout=None):
        """return an item from the queue 
        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""

        if block:
            item = self.__db.brpoplpush(self.key, self.key_process, timeout=timeout)
        else:
            item = self.__db.rpoplpush(self.key, self.key_process)
        
        if not item:
            raise Empty 
     
        return self.__unserialize(item)

    def get_nowait(self):
        """Equivalent to get(False)."""
        
        return self.get(False)

    def task_done(self, item):
        """Task is done"""
        
        item = self.__serialize(item)  
        ret = self.__db.lrem(self.key_process, -1, item)>0
                     
        return ret
        
    def join(self):
        """Blocks until all items in the Queue have been gotten and processed"""
    
        while self.__db.llen(self.key_process)>0:
            _sleep(0.1)     

    def exists(self, item, no_cache = True):  
        """Check if item exists in usual or processing queues i.e.
        it returns True for not acquired item and also for item which was acquired but for which wasn't called task_done method.
        Data is approximately and cached """
        
        item = self.__serialize(item)
        hash = hashlib.md5(item).hexdigest()
        
        if no_cache or self.exists_cache is None:
            self.exists_cache = {}
            data = self.__db.lrange(self.key, 0, -1)
            for i, datum in enumerate(data):
                datum = hashlib.md5(datum).hexdigest()
                if datum in self.exists_cache.keys():
                    self.exists_cache[datum] += 1
                else:
                    self.exists_cache[datum] = 1
            data = self.__db.lrange(self.key_process, 0, -1)
            for i, datum in enumerate(data):
                datum = hashlib.md5(datum).hexdigest()
                if datum in self.exists_cache.keys():
                    self.exists_cache[datum] += 1
                else:
                    self.exists_cache[datum] = 1

        return hash in self.exists_cache.keys()

    def clear_all(self):   
        """Clear all queues"""
        
        return bool(self.__db.delete(self.key, self.key_process))

    def clear_process(self):   
        """Clear process queue"""
        
        return bool(self.__db.delete(self.key_process))        
