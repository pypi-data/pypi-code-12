from ._fs import Vlermv
try:
    import boto
except ImportError:
    pass
else:
    del(boto)
    from ._s3 import S3Vlermv
from . import serializers, transformers

# For backwards compatibility
cache = Vlermv.memoize
