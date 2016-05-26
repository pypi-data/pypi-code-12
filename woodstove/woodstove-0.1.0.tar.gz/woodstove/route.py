from woodstove import hooks


def _default_formatter(req):
    hooks.call_hooks('route', 'formatter', req)

    if not isinstance(req.ret, (list, tuple)):
        req.ret = (req.ret,)

    if req.total is None:
        req.total = len(req.ret)

    return {'data': req.ret,
            'total': req.total}


class Route(object):
    auth = False
    acl = None
    body_args = None
    query_args = None

    def __init__(self, path, method, func, options):
        self.path = path
        self.method = method
        self.fname = func.__name__
        self.mname = func.__module__
        self.func = func
        self.options = options
        self.format_fn = options.get('formatter', _default_formatter)

        if self.format_fn is None:
            self.format_fn = lambda x: x.ret
