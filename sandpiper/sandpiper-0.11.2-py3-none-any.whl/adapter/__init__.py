import re

from .inmemory  import InMemory

try:
    from .dynamodb  import DynamoDB
    from .memcached import Memcached
    from .memcached import get_default_client as create_memcached_client
    from .xredis    import Adapter            as Redis
    from .xredis    import create_client      as create_redis_client
except ImportError as e:
    if not re.search("No module named", str(e)):
        raise e
