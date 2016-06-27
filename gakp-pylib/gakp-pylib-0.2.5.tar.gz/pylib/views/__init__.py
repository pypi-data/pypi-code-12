from pylib.validation import schemas

from bson import ObjectId
import falcon
import functools
import json


class FalconResource(object):
    """Instances of this class are used to register url to the api.

    Request handlers in each of the abstractions are attached to the
    instance.
    """
    pass


class FalconAbstraction(object):
    """Abstract away the view of a web server.

    Hide validation, argument extraction and serialization from the
    main duty which is to handle cruds(create, read, update, delete, search)
    operations on an entity. The handlers are passed parameter from both
    the request context and the url parameters in kwargs form. It is recommended
    that all handlers registered on an abstraction have a keyword parameter kwargs
    to handle parameters it doesn't need.

    Args:
        path (str): Url to be registered with falcon as the
            address for the collections. All url parameters specified
            in this path will be passed to all responders that are
            registered in the `kwargs` parameter if specified
        schema (marshmallow.Schema): the abstraction's schema for serializing,
            deserializing and validating request data.
        before (list of function): Decorators to be called before
            every responder connected to this abstraction
        after (list of function): Decorators to be called after every
            responder connected to this abstraction.
    """

    def __init__(self, path, schema, before=[], after=[]):
        self.path = path
        self.schema = schema
        self.before = before
        self.after = after
        self.resource = FalconResource()


def setup_hooks(handler, before, after):
    """Setup the handlers before and after hooks."""
    handler = functools.reduce(lambda x, y: y(x), map(falcon.before, before), handler)
    handler = functools.reduce(lambda x, y: y(x), map(falcon.after, after), handler)
    return handler


def int_id_hook(idname):
    """Cast the idname parameter in the url to an int."""
    def hook(req, resp, res, params):
        try:
            params[idname] = int(params[idname])
        except ValueError:
            falcon.HTTPBadReuest('Invalid id', 'ID is not valid')
    return hook


def object_id_hook(idname):
    """Cast the idname parameter in the url to an int."""
    def hook(req, resp, res, params):
        try:
            params[idname] = ObjectId(params[idname])
        except ValueError:
            falcon.HTTPBadReuest('Invalid id', 'ID is not valid')
    return hook


def auth_hook(inet_client):
    def hook(req, resp, res, params):
        auth_token = req.cookies.get('auth')
        if auth_token is None:
            raise falcon.HTTPUnauthorized('Authorization required!!', 'Please login first')

        data, errors = inet_client.get('admin.tokens.verify', dict(token=auth_token))
        if errors:
            raise falcon.HTTPForbidden('Invalid token', errors[0])
        req.context['user'] = data
    return hook


def response(response, schema, data, many=False):
    response.content_type == 'application/json'
    data = schemas.dump(schema, data, many=many)
    response.body = json.dumps(data)


def register(abstraction, api):
    """Link the abstraction and the falcon API instance."""
    api.add_route(abstraction.path, abstraction.resource)
