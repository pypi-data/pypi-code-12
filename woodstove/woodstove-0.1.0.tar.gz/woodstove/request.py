import six
import time
import uuid
import bottle


class Request(object):
    exception = None
    exception_handled = False
    ret = None
    total = None
    query = None
    body = None
    user = None

    def __init__(self, robj, args, kwargs):
        self.robj = robj
        self.args = args
        self.kwargs = kwargs
        self.request = bottle.request
        self.response = bottle.response
        self.uuid = six.text_type(uuid.uuid4())
        self.start = time.time()

    def formatter(self):
        return self.robj.format_fn(self)
