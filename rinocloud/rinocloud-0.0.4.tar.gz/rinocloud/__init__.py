# Rinocloud Python bindings
# API docs at http://github.com/rinocloud/rinocloud-python
# Authors:
# Jamie Lee <jamie@rinocloud.com>
# Eoin Murray <eoin@rinocloud.com>

api_key = None
api_domain = 'https://rinocloud.com/'
api_base = '%s/api/1/' % api_domain

path = ''

from .config import *
from .object import Object
from .collection import Collection
from .query import Query
from .batch import Batch
from . import http

set_rinocloud_urls()
