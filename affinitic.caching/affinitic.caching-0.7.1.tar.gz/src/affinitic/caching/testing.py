from plone.testing import Layer
from affinitic.caching.memcached import activate_memcached_usage
from affinitic.caching.memcached import deactivate_memcached_usage


class NoMemcached(Layer):

    def setUp(self):
        deactivate_memcached_usage()

    def tearDown(self):
        activate_memcached_usage()


NO_MEMCACHED = NoMemcached(name="NO_MEMCACHED")
