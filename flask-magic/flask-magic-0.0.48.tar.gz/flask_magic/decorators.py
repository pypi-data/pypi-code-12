import functools
import inspect
from flask import Response, jsonify, abort, request, current_app
from werkzeug.wrappers import BaseResponse
from core import Magic, init_app
from dicttoxml import dicttoxml
import ext
import copy

__all__ = [
    "route",
    "menu",
    "template",
    "plugin",
    "methods",
    "render_as_json",
    "render_as_xml",
    "require_user_roles",
    "login_required",
    "no_login_required",
]
# ------------------------------------------------------------------------------
def plugin(module, *args, **kwargs):
    """
    Decorator to extend a package to a view.
    The module can be a class or function. It will copy all the methods to the class

    ie:
        # Your module.py
        my_ext(view, **kwargs):
            class MyExtension(object):
                def my_view(self):
                    return {}

            return MyExtension

        # Your view.py
        @plugin(my_ext)
        class Index(Magic):
            pass

    :param module: object
    :param args:
    :param kwargs:
    :return:
    """
    def wrap(f):
        m = module(f, *args, **kwargs)
        if inspect.isclass(m):
            for k, v in m.__dict__.items():
                if not k.startswith("__"):
                    setattr(f, k, v)
        elif inspect.isfunction(m):
            setattr(f, kls.__name__, m)
        return f
    return wrap


def route(rule=None, **kwargs):
    """
    This decorator defines custom route for both class and methods in the view.
    It behaves the same way as Flask's @app.route

    on class:
        It takes the following args
            - rule: the root route of the endpoint
            - decorators: a list of decorators to run on each method

    on methods:
        along with the rule, it takes kwargs
            - endpoint
            - defaults
            - ...

    :param rule:
    :param kwargs:
    :return:
    """

    _restricted_keys = ["extends", "route", "decorators"]
    def decorator(f):
        if inspect.isclass(f):
            extends = kwargs.pop("extends", None)
            if extends and hasattr(extends, self.view_key):
                for k, v in getattr(extends, self.view_key).items():
                    kwargs.setdefault(k, v)

            kwargs.setdefault("route", rule)
            kwargs["decorators"] = kwargs.get("decorators", []) + f.decorators
            setattr(f, "_route_extends__", kwargs)
            setattr(f, "base_route", kwargs.get("route"))
            setattr(f, "decorators", kwargs.get("decorators", []))
        else:
            if not rule:
                raise ValueError("'rule' is missing in @route ")

            for k in _restricted_keys:
                if k in kwargs:
                    del kwargs[k]

            # Put the rule cache on the method itself instead of globally
            if not hasattr(f, '_rule_cache') or f._rule_cache is None:
                f._rule_cache = {f.__name__: [(rule, kwargs)]}
            elif not f.__name__ in f._rule_cache:
                f._rule_cache[f.__name__] = [(rule, kwargs)]
            else:
                f._rule_cache[f.__name__].append((rule, kwargs))
        return f

    return decorator


def methods(*meth):
    """
    To explicitely set the methods to use without using @route
    This can only be applied of methods. Not class.

    :param meth: tuple of available method
    :return:
    """
    def decorator(f):
        if not hasattr(f, '_methods_cache'):
            f._methods_cache = [m.upper() for m in meth]
        return f
    return decorator

def template(page=None, layout=None, **kwargs):
    """
    Decorator to change the view template and layout.

    It works on both Magic class and view methods

    on class
        only $layout is applied, everything else will be passed to the kwargs
        Using as first argument, it will be the layout.

        :first arg or $layout: The layout to use for that view
        :param layout: The layout to use for that view
        :param kwargs:
            get pass to the TEMPLATE_CONTEXT

    ** on method that return a dict
        page or layout are optional

        :param page: The html page
        :param layout: The layout to use for that view

        :param kwargs:
            get pass to the view as k/V

    ** on other methods that return other type, it doesn't apply

    :return:
    """
    pkey = "_template_extends__"

    def decorator(f):
        if inspect.isclass(f):
            layout_ = layout or page
            extends = kwargs.pop("extends", None)
            if extends and hasattr(extends, pkey):
                items = getattr(extends, pkey).items()
                if "layout" in items:
                    layout_ = items.pop("layout")
                for k, v in items:
                    kwargs.setdefault(k, v)
            if not layout_:
                layout_ = "layout.html"
            kwargs.setdefault("brand_name", "")
            kwargs["layout"] = layout_

            setattr(f, pkey, kwargs)
            setattr(f, "base_layout", kwargs.get("layout"))
            f.g(TEMPLATE_CONTEXT=kwargs)
            return f
        else:
            @functools.wraps(f)
            def wrap(*args2, **kwargs2):
                response = f(*args2, **kwargs2)
                if isinstance(response, dict) or response is None:
                    response = response or {}
                    if page:
                        response.setdefault("template_", page)
                    if layout:
                        response.setdefault("layout_", layout)
                    for k, v in kwargs.items():
                        response.setdefault(k, v)
                return response
            return wrap
    return decorator

# ------------------------------------------------------------------------------
"""
VIEW RENDERING DECORATORS

It allows you quickly switch the rendering view of a method.
For it to work all methods must return a dict. Even empty.
By default it will render the page as template


    class Index(Magic):

        @render_as_json
        def index2():
            retun {}

        @render_as_xml
        def index():
            retun {}

"""
# Helper function to normalize view return values .
# It always returns (dict, status, headers). Missing values will be None.
# For example in such cases when tuple_ is
#   (dict, status), (dict, headers), (dict, status, headers),
#   (dict, headers, status)
#
# It assumes what status is int, so this construction will not work:
# (dict, None, headers) - it doesn't make sense because you just use
# (dict, headers) if you want to skip status.
def _normalize_response_tuple(tuple_):
    v = tuple_ + (None,) * (3 - len(tuple_))
    return v if isinstance(v[1], int) else (v[0], v[2], v[1])


# Helper function to create JSON response for the given data.
# Raises an error if the data is not convertible to JSON.
def _build_response(data, renderer=None):
    if isinstance(data, Response) or isinstance(data, BaseResponse):
        return data
    if not renderer:
        raise AttributeError(" Renderer is required")
    if isinstance(data, dict) or data is None:
        data = {} if data is None else data
        return renderer(data), 200
    elif isinstance(data, tuple):
        data, status, headers = _normalize_response_tuple(data)
        return renderer(data or {}), status, headers
    else:
        raise ValueError('Unsupported return value.')

json_renderer = lambda i, data: _build_response(data, jsonify)
xml_renderer = lambda i, data: _build_response(data, dicttoxml)

def render_as_json(func):
    """
    Decorator to render as JSON
    :param func:
    :return:
    """
    if inspect.isclass(func):
        setattr(func, "_renderer", json_renderer)
        return func
    else:
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            data = func(*args, **kwargs)
            return _build_response(data, jsonify)
        return decorated_view

def render_as_xml(func):
    """
    Decorator to render as XML
    :param func:
    :return:
    """
    if inspect.isclass(func):
        setattr(func, "_renderer", xml_renderer)
        return func
    else:
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            data = func(*args, **kwargs)
            return _build_response(data, dicttoxml)
        return decorated_view


# ------------------------------------------------------------------------------
class Menu(object):
    """
    PageMenu is class decorator to build page menu while building the enpoints

    Decorator to build navigation menu directly on the methods
    By default it will build the menu of the module, class an method
    If the class is also decorated, it will use the menu _name as the top level _name

    :param title: The menu title
    :param kwargs: extra options to pass into the menu or to move the menu somewhere else

        order int: The order of the menu in the set

        visible (list of bool or callback): To hide and show menu. Accepts bool or
                    list of callback function the callback function must return
                    a bool to check if all everything is True to show or will be False
                    ** When this menu is inside of a menu set, or has parent, if you want
                    that page to be activated, but don't want to create a menu link,
                    for example: a blog read page, set show to False. It will know
                    the menu set is active

        *** alias to visible
            visible_with_auth_user: (bool) : it will check if current_user is authenticated

        endpoint string: By default the endpoint is built based on the method and class.
                    When set it will be used instead

        endpoint_kwargs dict: dict of k/v data for enpoint

        group_name str: On class menu, it can be used to filter a menu set to display.
                    If a class is passed, it will try to inherit the group from that class

        The args below will allow you to change where the menu is placed.
        By default they are set automatically

        module_: the module _name. Usually if using another module
        class_: the class _name class _name in the module
        method_: The method _name, to build endpoint. Changing this will change the url

        extends: class Name. To use the extends of the class

        some other kwargs:
            url
            target
            fa_icon
            align_right
            show_profile_avatar
            show_profile_name
    :return:
    """
    def __call__(self, title, **kwargs):

        def wrap(f):
            if title:
                module_ = kwargs.pop("module_", f.__module__)
                class_ = kwargs.pop("class_", inspect.stack()[1][3])
                method_ = kwargs.pop("method_", f.__name__)
                is_class_ = inspect.isclass(f)

                if "visible_with_auth_user" in kwargs:
                    kwargs["visible"] = ext.user_authenticated \
                        if kwargs["visible_with_auth_user"] is True \
                        else ext.user_not_authenticated

                extends = kwargs.pop("extends", None)
                if extends:
                    if is_class_:
                        extendscls = self.get(extends)
                        if extendscls and "kwargs" in extendscls:
                            if "group_name" not in kwargs:
                                kwargs["group_name"] = extendscls["kwargs"]["group_name"]
                            if "visible" not in kwargs:
                                kwargs["visible"] = extendscls["kwargs"]["visible"]
                    else:
                        if "endpoint" not in kwargs:
                            endpoint = "%s:%s" % (class_, f.__name__)
                            kwargs["endpoint"] = endpoint
                    module_ = extends.__module__
                    class_ = extends.__name__

                self._push(module_=module_,
                           class_=class_,
                           method_=method_,
                           title=title,
                           is_class_=is_class_,
                           **kwargs)
            return f
        return wrap

    def __init__(self):
        self.MENU = {}

    def add(self, title, extends, **kwargs):
        """
        To manually add a extends. Usually, menu by hand which
        may not be attached to any functions
        :param title:
        :param cls:
        :param method_:
        :param is_class_:
        :param kwargs:
        :return:
        """
        f = extends
        self._push(title=title,
                   module_=f.__module__,
                   class_=f.__name__,
                   method_=f.__name__,
                   is_class_=False,
                   **kwargs)

    def clear(self):
        self.MENU = {}

    def _push(self, **kwargs):

        module_ = kwargs.pop("module_")
        class_ = kwargs.pop("class_")
        method_ = kwargs.pop("method_")
        is_class_ = kwargs.pop("is_class_")

        __cls = method_ if is_class_ else class_
        path = "%s.%s" % (module_, __cls)

        if path not in self.MENU:
            self.MENU[path] = {
                "title": None,
                "endpoint": None,
                "endpoint_kwargs": {},
                "order": None,
                "sub_menu": [],
                "kwargs": {}
            }

        if "title" not in kwargs:
            raise TypeError("Missing 'title' in menu decorator")

        _endpoint = "%s:%s" % (__cls,"index" if is_class_ else method_)
        kwargs["endpoint"] = kwargs.pop("endpoint", _endpoint)
        kwargs["endpoint_kwargs"] = kwargs.pop("endpoint_kwargs", {})
        order = kwargs.pop("order", 0)
        title = kwargs.pop("title")
        endpoint = kwargs.pop("endpoint")

        # visible: accepts a bool or list of callback to execute
        visible = kwargs.pop("visible", [True])
        if not isinstance(visible, list):
            visible = [visible]

        kwargs["visible"] = visible
        kwargs["active"] = None
        kwargs["index"] = None

        if is_class_:  # class menu
            kwargs["endpoint"] = endpoint
            kwargs["group_name"] = kwargs.pop("group_name", None)
            kwargs["has_submenu"] = True
            self.MENU[path]["title"] = title
            self.MENU[path]["order"] = order
            self.MENU[path]["kwargs"] = kwargs

        else:  # sub menu
            kwargs["has_submenu"] = False
            menu = (order, title, endpoint, kwargs)
            self.MENU[path]["sub_menu"].append(menu)

    def _test_visibility(self, shows):
        if isinstance(shows, bool):
            return shows
        elif not isinstance(shows, list):
            shows = [shows]
        return all([x() if hasattr(x, "__call__") else x for x in shows])

    def get(self, cls):
        key = self.get_key(cls)
        return self.MENU[key]

    def get_key(self, cls):
        """
        Return the string key of the class
        :param cls: class
        :return: str
        """
        return "%s.%s" % (cls.__module__, cls.__name__)

    def get_extends(self, f):
        return dict(module_=f.__module__, class_=f.__name__)

    def render(self):
         # (order, Name, sub_menu, **kargs, hidden_submenu)
        menu_list = []
        menu_index = 0
        for _, menu in copy.deepcopy(self.MENU.items()):
            menu_index += 1
            sub_menu = []

            menu["kwargs"]["index"] = menu_index
            menu["kwargs"]["active"] = False
            if "visible" in menu["kwargs"]:
                menu["kwargs"]["visible"] = self._test_visibility(menu["kwargs"]["visible"])

            for s in menu["sub_menu"]:
                if s[2] == request.endpoint:
                    s[3]["active"] = True
                    menu["kwargs"]["active"] = True
                s[3]["visible"] = self._test_visibility(s[3]["visible"])
                sub_menu.append(s)

            _kwargs = menu["kwargs"]

            if menu["title"]:
                menu_list.append((
                    menu["order"],
                    menu["title"],
                    sorted(sub_menu),
                    _kwargs
                ))
            else:
                menu_list += sub_menu
        return sorted(menu_list)

    def init_app(self, app):
        @app.before_request
        def p(*args, **kwargs):
            if request.endpoint not in ["static", None]:
                # (order, Name, sub_menu, **kargs, hidden_submenu)
                Magic.g(MENU=menu.render())

menu = Menu()
init_app(menu.init_app)

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

def require_user_roles(*roles):
    """
    A decorator to check if user has any of the roles specified

    @require_user_roles('superadmin', 'admin')
    def fn():
        pass
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if ext.user_authenticated():
                if not ext.flask_login.current_user.has_any_roles(*roles):
                    return abort(403)
            else:
                return abort(401)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def with_user_permissions(*permissions):
    pass

def login_required(func):
    """
    A wrapper around the flask_login.login_required.
    But it also checks the presence of the decorator: @no_login_required
    On a "@login_required" class, method containing "@no_login_required" will
    still be able to access without authentication
    :param func:
    :return:
    """
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if "no_login_required" not in ext.utils.get_decorators_list(func) \
                and ext.user_not_authenticated():
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

def no_login_required(func):
    """
    Dummy decorator. @login_required will inspect the method
    to look for this decorator
    Use this decorator when you want do not require login in a "@login_required" class/method
    :param func:
    :return:
    """
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        return func(*args, **kwargs)
    return decorated_view

# ------------------------------------------------------------------------------
# todo

def headers(headers={}):
    """This decorator adds the headers passed in to the response
    http://flask.pocoo.org/snippets/100/
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator

def noindex(f):
    """This decorator passes X-Robots-Tag: noindex
    http://flask.pocoo.org/snippets/100/
    """
    return headers({'X-Robots-Tag': 'noindex'})(f)

def crossdomain(origin=None,
                methods=None,
                headers=None,
                max_age=21600,
                attach_to_all=True,
                automatic_options=True):
    """

    :param origin: '*' to allow all origins, otherwise a string with a URL
            or a list of URLs that might access the resource.
    :param methods: Optionally a list of methods that are allowed for this
            view. If not provided it will allow all methods that are implemented
    :param headers: Optionally a list of headers that are allowed for this request.
    :param max_age: The number of seconds as integer or timedelta object
            for which the preflighted request is valid.
    :param attach_to_all: True if the decorator should add the access control
            headers to all HTTP methods or False if it should only add them to
            OPTIONS responses.
    :param automatic_options: If enabled the decorator will use the default
            Flask OPTIONS response and attach the headers there,
            otherwise the view
    :return:

    http://flask.pocoo.org/snippets/56/
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    else:
        options_resp = current_app.make_default_options_response()
        methods = options_resp.headers['allow']

    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = methods
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def jsonp(func):
    """Wraps JSONified output for JSONP requests.
    http://flask.pocoo.org/snippets/79/
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


