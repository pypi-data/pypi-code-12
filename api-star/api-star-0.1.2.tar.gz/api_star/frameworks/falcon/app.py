from api_star.core import check_permissions, render
from api_star.exceptions import APIException, NotAcceptable
from api_star.frameworks.falcon.request import APIRequest
from api_star.frameworks.falcon.response import APIResponse
from api_star.schema import get_link
from collections import namedtuple
import coreapi
import falcon


def error_handler(exc, request, response, params):
    try:
        request.renderer
    except NotAcceptable as exc:
        pass

    data = {'message': exc.description}
    content, content_type = render(request, data)
    if content_type:
        response.set_header('Content-Type', content_type)
    response.body = content
    response.status = str(exc.code)  # TODO: Blergh


class App(falcon.API):
    request_class = APIRequest
    response_class = APIResponse

    def __init__(self, module=None, **kwargs):
        self._registered = {}
        self.links = {}
        self.title = kwargs.pop('title', None)
        self.parsers = kwargs.pop('parsers', None)
        self.renderers = kwargs.pop('renderers', None)
        self.authenticators = kwargs.pop('authenticators', None)
        self.permissions = kwargs.pop('permissions', None)
        if 'request_type' not in kwargs:
            kwargs['request_type'] = App.request_class
        super(App, self).__init__(**kwargs)
        self.add_error_handler(APIException, error_handler)

    def get(self, url, **options):
        return self.api_route(url, 'GET', **options)

    def post(self, url, **options):
        return self.api_route(url, 'POST', **options)

    def put(self, url, **options):
        return self.api_route(url, 'PUT', **options)

    def patch(self, url, **options):
        return self.api_route(url, 'PATCH', **options)

    def delete(self, url, **options):
        return self.api_route(url, 'DELETE', **options)

    def api_route(self, url, method, **options):
        tag = options.pop('tag', None)
        exclude_from_schema = options.pop('exclude_from_schema', False)
        renderers = options.pop('renderers', self.renderers)
        parsers = options.pop('parsers', self.parsers)
        authenticators = options.pop('authenticators', self.authenticators)
        permissions = options.pop('permissions', self.permissions)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)
            func.link = get_link(url, method, func)

            if not exclude_from_schema:
                if tag:
                    if tag not in self.links:
                        self.links[tag] = {}
                    self.links[tag][endpoint] = func.link
                else:
                    self.links[endpoint] = func.link
                self.schema = coreapi.Document(title=self.title, content=self.links)

            def wrapper(request, response, **params):
                for field in func.link.fields:
                    if field.location == 'form':
                        if field.name in request.data:
                            params[field.name] = request.data[field.name]
                    elif field.location == 'query':
                        if field.name in request.params:
                            params[field.name] = request.params[field.name]
                    elif field.location == 'body':
                        params[field.name] = request.data

                if renderers is not None:
                    request.renderers = renderers
                if parsers is not None:
                    request.parsers = parsers
                if authenticators is not None:
                    request.authenticators = authenticators

                if permissions is not None:
                    check_permissions(request, permissions)

                data = func(**params)

                # TODO: Handle case where APIResponse is returned.
                content, content_type = render(request, data)
                if content_type is not None:
                    response.set_header('Content-Type', content_type)
                response.body = content

            # Setup the app routing each time `@app.<method>()` is called.
            if url not in self._registered:
                self._registered[url] = {}
            self._registered[url][method] = wrapper
            self._router._roots = []
            self._setup()
            return func
        return decorator

    def _setup(self):
        for url, methods in self._registered.items():
            resource = {}
            for method, func in methods.items():
                method_function = "on_{0}".format(method.lower())
                resource[method_function] = func
            resource = namedtuple('Resource', resource.keys())(**resource)
            self.add_route(url, resource)
