# Rinocloud Python bindings
# API docs at http://github.com/rinocloud/rinocloud-python
# Authors:
# Jamie Lee <jamie@rinocloud.com>
# Eoin Murray <eoin@rinocloud.com>

api_key = None

api_domain = 'https://rinocloud.com/'

api_base = '%s/api/1/' % api_domain
path = None

from config import *
from object import Object
from query import Query
import http as http


urls = {
    'upload': api_base + 'files/upload_multipart/',
    'upload_meta': api_base + 'files/create_object/',
    'get_metadata': api_base + 'files/get_metadata/',
    'update': api_base + 'files/update_metadata/',
    'download': api_base + 'files/download/?id=',
    'query': api_base + 'files/query/',
    'sign_s3': api_base + 'files/sign_s3/',
    'pre_s3_upload': api_base + 'files/pre_s3_upload/',
    'post_s3_upload': api_base + 'files/post_s3_upload/',
}
