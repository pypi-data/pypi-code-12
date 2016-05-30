from .actions import (ActionFunction, ActionList, current_context, ContextExitException,\
                     ensure_context)
from .decorators import WithActionsDecorator, register_hooks, preprend_base_url_to_expose
from .views import Blueprint, as_view, ActionsView, full_exec_request_actions
from .request import process_request_params
from .utils import logger
from flask import Response, json, request, current_app, jsonify, abort, make_response
from werkzeug.local import LocalProxy
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response as WResponse
import inspect
import functools


class ServiceActionsView(ActionsView):
    """View class for service views created using the ServiceLoader
    """
    def dispatch_request(self, *args, **kwargs):
        rv = super(ServiceActionsView, self).dispatch_request(*args, **kwargs)
        # child actions can use "return" to return a value which
        # can be something else than a proper Response instance.
        # In this case we encode the return value to json
        if isinstance(rv, (Response, WResponse)):
            return rv
        return json.dumps(rv), {'Content-Type': current_app.config.get(
            'SERVICES_CONTENT_TYPE', 'application/json;charset=UTF-8')}

    def execute_actions(self, *args, **kwargs):
        func = None
        if self.func:
            func = lambda: self.func(*args, **kwargs)
        def render():
            # the render func is only called if the actions do not
            # exit the context, thus we return an empty json response
            return jsonify()
        return full_exec_request_actions(self.actions, func=func,
            marshaller=self.marshall, render_func=render)


def patch_action(action):
    """This will add raising TriggerActionGroupException when api_success
    or api_error have been used. This allows nice logic flows when using
    a service as an action
    """
    old_execute = action.execute
    def execute(self):
        with ensure_context():
            try:
                if old_execute(self):
                    current_context.trigger_action_group(action.name + "_success")
            except ServiceError as e:
                current_context['service_error'] = e
                current_context.trigger_action_group(action.name + "_error")
    action.execute = execute
    return action


def wrap_view_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServiceError as e:
            return make_response(json.dumps({"error": e.message}), e.http_code)
    for attr in ('request_params', 'marshall_with'):
        if hasattr(func, attr):
            setattr(wrapper, attr, getattr(func, attr))
    return wrapper


def get_current_app_service(name):
    return current_app.services[name]


_services_proxies = {}

def service_proxy(name):
    if name not in _services_proxies:
        _services_proxies[name] = LocalProxy(lambda: get_current_app_service(name))
    return _services_proxies[name]


def pass_service(*names):
    """Injects a service instance into the kwargs
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for name in names:
                kwargs[name] = service_proxy(name)
            return f(*args, **kwargs)
        return wrapper
    return decorator


class ServiceError(Exception):
    def __init__(self, message, http_code=500):
        self.message = message
        self.http_code = http_code


class ServiceMeta(type):
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls.current = service_proxy(attrs.get('name') or name)


class Service(object):
    name = None
    view_class = ServiceActionsView
    blueprint_class = Blueprint
    url_prefix = None
    __metaclass__ = ServiceMeta

    def __init__(self):
        self.name = self.name or self.__class__.__name__
        self.actions = ActionList()
        self.views = []
        self.hooks = []
        for attr in dir(self):
            attr = getattr(self, attr)
            if isinstance(attr, ActionFunction):
                self.actions.append(patch_action(attr.action))
                if hasattr(attr, 'urls'):
                    preprend_base_url_to_expose(self.url_prefix, attr)
                    func = attr.unbound_func if isinstance(attr.unbound_func, WithActionsDecorator) else attr.func
                    view_func = wrap_view_func(func)
                    self.views.append(as_view(name=attr.unbound_func.__name__, url_rules=attr.urls, view_class=self.view_class)(view_func))
            elif hasattr(attr, 'urls'):
                preprend_base_url_to_expose(self.url_prefix, attr)
                view_func = wrap_view_func(attr)
                self.views.append(as_view(name=attr.__name__, url_rules=attr.urls, view_class=self.view_class)(view_func))
            elif hasattr(attr, 'hooks'):
                self.hooks.append(attr)

    @property
    def exposed(self):
        return len(self.views) > 0 or len(self.hooks) > 0

    @property
    def blueprint_name(self):
        return "%s_service" % self.name

    def as_blueprint(self):
        bp = self.blueprint_class(self.blueprint_name, self.__class__.__module__)
        for view in self.views:
            bp.add_view(view)
        for attr in self.hooks:
            register_hooks(attr, attr.hooks, bp)
        return bp