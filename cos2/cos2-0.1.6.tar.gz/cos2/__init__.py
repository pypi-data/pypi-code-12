__version__ = '0.1.6'

from . import models, exceptions

from .api import Service, Bucket
from .auth import Auth, AnonymousAuth
from .http import Session, CaseInsensitiveDict


from .iterators import (BucketIterator, ObjectIterator,
                        MultipartUploadIterator, PartIterator)


from .compat import to_bytes, to_string, to_unicode, urlparse, urlquote, urlunquote
from .utils import content_type_by_name, is_valid_bucket_name
from .utils import http_date, http_to_unixtime, iso8601_to_unixtime, date_to_iso8601, iso8601_to_date,determine_part_size,SizedFileAdapter


from .models import BUCKET_ACL_PRIVATE, BUCKET_ACL_PUBLIC_READ
from .models import OBJECT_ACL_DEFAULT, OBJECT_ACL_PRIVATE, OBJECT_ACL_PUBLIC_READ, OBJECT_ACL_PUBLIC_READ_WRITE


