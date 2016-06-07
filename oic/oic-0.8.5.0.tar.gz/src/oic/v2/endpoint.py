class Endpoint(object):
    name = ''

    def __init__(self, req_cls, resp_cls, **kwargs):
        self.req_cls = req_cls
        self.resp_cls = resp_cls
        self.server = None

    def parse_request(self, *args, **kwargs):
        pass

    def endpoint(self, *args, **kwargs):
        pass

    def register(self, srv):
        setattr(srv, 'parse_{}_request'.format(self.name), self.parse_request)
        setattr(srv, '{}_endpoint'.format(self.name), self.endpoint)
        self.server = srv

