from flask import Response, jsonify


class ServiceResponse(Response):

    def __init__(self, **kwargs):
        if 'direct_passthrough' not in kwargs:
            kwargs['direct_passthrough'] = True
        super(ServiceResponse, self).__init__(**kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(ServiceResponse, cls).force_type(rv, environ)
