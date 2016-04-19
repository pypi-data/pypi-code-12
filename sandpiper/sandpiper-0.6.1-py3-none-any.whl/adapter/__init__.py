import re

try:
    from .dynamodb import DynamoDB
except ImportError as e:
    if not re.search("No module named 'boto3'", str(e)):
        raise e

from .inmemory  import InMemory
from .dynamodb  import DynamoDB
from .memcached import Memcached
from .memcached import get_default_client as create_memcached_client
from .xredis    import Adapter            as Redis
from .xredis    import create_client      as create_redis_client
