"""
Magic

"""

import re
import os
import sys
import inspect
import datetime
import functools
import logging
import logging.config
import utils
import copy
import exceptions
from six import string_types
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import BaseConverter, parse_rule
from werkzeug.exceptions import Aborter
from flask import (Flask, g, render_template, flash, session, url_for, request,
                   redirect, make_response, Response)
from flask_assets import Environment
import jinja2
from __about__ import *


_py2 = sys.version_info[0] == 2
# ------------------------------------------------------------------------------

__all__ = [
            "Magic",
            "MagicWand",
            "get_env",
            "set_env",
            "get_env_config",
            "get_config",
            "set_meta",
            "abort",
            "flash_data",
            "get_flashed_data",
            "init_app",
            "register_package",

            # For convenience when importing from flask_magic, but can use
            # the flask one
            "flash",
            "session",
            "url_for",
            "request",
            "redirect"
           ]


__ENV__ = None


def get_env():
    """
    Return the Capitalize environment name
    It can be used to retrieve class base config
    Default: Development
    :returns: str Capitalized
    """
    env = __ENV__ \
          or (os.environ["env"] if "env" in os.environ else "Development")
    return env.lower().capitalize()


def set_env(env):
    """
    Set the envrionment manually
    :param env:
    :return:
    """
    global __ENV__
    __ENV__ = env


def get_env_config(config):
    """
    Return config class based based on the config
    :param config : Object - The configuration module containing the environment object
    """
    return getattr(config, get_env())


def init_app(kls):
    """
    To bind middlewares, plugins that needs the 'app' object to init
    Bound middlewares will be assigned on cls.init()
    """
    if not hasattr(kls, "__call__"):
        raise TypeError("init_app: '%s' is not callable" % kls)
    Magic._init_apps.add(kls)
    return kls


def register_package(pkg):
    """
    Allow to register packages by loading and exposing: templates, static,
    and exceptions for abort()

    Structure of package
        root
            | $package_name
                | __init__.py
                |
                | exceptions.py
                |
                | /templates
                    |
                    |
                |
                | /static
                    |
                    | assets.yml

    :param pkg: str - __package__
                    or __name__
                    or The root dir
                    or the dotted resource package (package.path.path,
                    usually __name__ of templates and static
    """

    root_pkg_dir = pkg
    if not os.path.isdir(pkg) and "." in pkg:
        root_pkg_dir = utils.get_pkg_resources_filename(pkg)

    template_path = os.path.join(root_pkg_dir, "templates")
    static_path = os.path.join(root_pkg_dir, "static")

    logging.info("Registering Package: " + pkg)
    if os.path.isdir(template_path):
        template_path = jinja2.FileSystemLoader(template_path)
        Magic._template_paths.add(template_path)

    if os.path.isdir(static_path):
        Magic._static_paths.add(static_path)
        Magic._add_asset_bundle(static_path)

    if os.path.isfile(os.path.join(root_pkg_dir, "exceptions.py")):
        exceptions = utils.import_string(pkg + ".exceptions")
        init_app(lambda x: abort.map_from_module(exceptions))


def flash_data(data):
    """
    Just like flash, but will save data
    :param data:
    :return:
    """
    session["_flash_data"] = data


def get_flashed_data():
    """
    Retrieved
    :return: mixed
    """
    return session.pop("_flash_data", None)


def get_config(key, default=None):
    """
    Shortcut to access the application's config in your class
    :param key: The key to access
    :param default: The default value when None
    :returns mixed:
    """
    return Magic._app.config.get(key, default)


def set_meta(**kwargs):
    """
    Meta allows you to add meta data to site
    :params **kwargs:

    meta keys we're expecting:
        title (str)
        description (str)
        url (str) (Will pick it up by itself if not set)
        image (str)
        site_name (str) (but can pick it up from config file)
        object_type (str)
        keywords (list)
        locale (str)
        card (str)

        **Boolean By default these keys are True
        use_opengraph
        use_twitter
        use_googleplus
python
    """
    page_meta = Magic._global.get("__META__", {})
    page_meta.update(**kwargs)
    Magic.g(__META__=page_meta)

# ------------------------------------------------------------------------------

# https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/exceptions.py
class CustomAborter(Aborter):
    """
    We'll modify abort, to also use the name of custom HTTPException classes
    """

    def __call__(self, code, *args, **kwargs):
        if isinstance(code, string_types) and code in self.mapping:
            raise self.get_exception(code)(*args, **kwargs)
        super(CustomAborter, self).__call__(code, *args, **kwargs)

    def get_exception(self, code):
        """
        Expose the class based on the code
        :param code:
        :return:
        """
        raise self.mapping[code]

    def map_from_module(self, module):
        """
        Map all classes the in $module with subclasses of exceptions.HTTPException
        to be called as as error in with abort()
        :param obj:
        :return:
        """
        maps = {}
        for name in dir(module):
            obj = getattr(module, name)
            try:
                if issubclass(obj, exceptions.HTTPException):
                    maps[name] = obj
            except TypeError as ter:
                pass
        self.mapping.update(maps)

abort = CustomAborter()
abort.map_from_module(exceptions)

# ------------------------------------------------------------------------------

#
class Magic(object):
    """Base view for any class based views implemented with Flask-Classy. Will
    automatically configure routes when registered with a Flask app instance.
    Credit: Shout out to Flask-Classy for the greatest logic in this class
    Flask-Classy -> https://github.com/apiguy/flask-classy
    """

    decorators = []
    base_route = None
    route_prefix = None
    trailing_slash = True
    base_layout = "layout.html"
    assets = None
    logger = None
    _app = None
    _init_apps = set()
    _template_paths = set()
    _static_paths = set()
    _asset_bundles = set()
    _default_page_meta = dict(
            title="",
            description="",
            url="",
            image="",
            site_name="",
            object_type="article",
            locale="",
            keywords=[],
            use_opengraph=True,
            use_googleplus=True,
            use_twitter=True,
            properties={}
        )
    _global = dict(
        __NAME__=__title__,
        __VERSION__=__version__,
        __YEAR__=datetime.datetime.now().year,
        __META__=_default_page_meta
    )

    @classmethod
    def __call__(cls,
                 flask_or_import_name,
                 project=None,
                 directory=None,
                 config=None,
                 exceptions=None,
                 compress_html=True,
                 exclude_views=False,
                 exclude_static=False,
                 exclude_templates=False):
        """
        Allow to register all subclasses of Magic at once

        If a class doesn't have a route base, it will create a dasherize version
        of the class name.

        So we call it once initiating
        :param flask_or_import_name: Flask instance or import name -> __name__
        :param project: name of the project. If the directory and config is empty, it will guess them from here
        :param directory: The directory containing your project's Views, Templates and Static
        :param config: string of config object. ie: "app.config.Dev"
        :param exceptions: The exceptions path to load
        :param compress_html: bool - If true it will use the plugin "htmlcompress"
                to remove white spaces off the html result
        :param exclude_views: bool - If true, it will setup everything but registering the views
        :param exclude_static: bool - If true, it will setup everything but registering the static
        :param exclude_templates: bool - If true, it will setup everything but registering the templates
        """

        if isinstance(flask_or_import_name, Flask):
            app = flask_or_import_name
        else:
            app = Flask(flask_or_import_name)

        app.wsgi_app = ProxyFix(app.wsgi_app)

        app.url_map.converters['regex'] = RegexConverter

        if not directory:
            directory = "application/%s" % project if project else "."

        if not config:
            config = "application.config.%s" % get_env()

        app.config.from_object(config)

        # Extensions to remove extra white spaces in html
        if compress_html:
            app.jinja_env.add_extension('flask_magic.extras.htmlcompress.HTMLCompress')

        if directory:
            app.template_folder = directory + "/templates"
            app.static_folder = directory + "/static"

        if exceptions:
            abort.map_from_module(exceptions)

        cls._app = app

        cls._setup_logger()

        if not exclude_static:
            cls._add_asset_bundle(app.static_folder)

        # Flask Assets
        cls.assets = Environment(cls._app)

        # Register templates
        if not exclude_templates:
            if cls._template_paths:
                loader = [cls._app.jinja_loader] + list(cls._template_paths)
                cls._app.jinja_loader = jinja2.ChoiceLoader(loader)

        # Register static
        if not exclude_static:
            if cls._static_paths:
                loader = [cls._app.static_folder] + list(cls._static_paths)
                cls.assets.load_path = loader

        # init_app
        [_app(cls._app) for _app in cls._init_apps]

        # Register all views
        if not exclude_views:
            for subcls in cls.__subclasses__():
                base_route = subcls.base_route
                if not base_route:
                    base_route = utils.dasherize(utils.underscore(subcls.__name__))
                    if subcls.__name__.lower() == "index":
                        base_route = "/"
                subcls.register(cls._app, base_route=base_route)

        # Load all bundles
        if not exclude_static:
            [cls.assets.from_yaml(a) for a in cls._asset_bundles]

        @cls._app.after_request
        def _after_request_cleanup(response):
            cls._global["__META__"] = cls._default_page_meta.copy()
            return response
        return cls._app

    @classmethod
    def render_(cls, data={}, template_=None, layout_=None, **kwargs):
        """
        To render data to the associate template file of the action view
        :param data: The context data to pass to the template
        :param template_: The file template to use. By default it will map the classname/action.html
        :param layout_: The body layout, must contain {% include __template__ %}
        """
        if not template_:
            stack = inspect.stack()[1]
            module = inspect.getmodule(cls).__name__
            module_name = module.split(".")[-1]
            action_name = stack[3]      # The method being called in the class
            view_name = cls.__name__    # The name of the class without View

            if view_name.endswith("View"):
                view_name = view_name[:-4]
            template_ = "%s/%s.html" % (view_name, action_name)

        data = data or dict()
        if kwargs:
            data.update(kwargs)
        data["__"] = cls._global
        data["__template__"] = template_

        return render_template(layout_ or cls.base_layout, **data)


    @classmethod
    def g(cls, **kwargs):
        """
        Assign a global view context to be used in the template
        :params **kwargs:
        """
        cls._global.update(kwargs)

    @classmethod
    def _add_asset_bundle(cls, path):
        """
        Add a webassets bundle yml file
        """
        f = "%s/assets.yml" % path
        if os.path.isfile(f):
            cls._asset_bundles.add(f)

    @classmethod
    def _setup_logger(cls):

        logging_config = cls._app.config["LOGGING_CONFIG"] \
            if "LOGGING_CONFIG" in cls._app.config else None
        if not logging_config:
            logging_cls = cls._app.config["LOGGING_CLASS"] \
                if "LOGGING_CLASS" in cls._app.config else "logging.StreamHandler"
            logging_config = {
                "version": 1,
                "handlers": {
                    "default": {
                        "class": logging_cls
                    }
                },
                'loggers': {
                    '': {
                        'handlers': ['default'],
                        'level': 'WARN',
                    }
                }
            }

        logging.config.dictConfig(logging_config)
        cls.logger = logging.getLogger("root")
        cls._app._logger = cls.logger
        cls._app._loger_name = cls.logger.name


    @classmethod
    def register(cls, app, base_route=None, subdomain=None, route_prefix=None,
                 trailing_slash=None):
        """Registers a Magic class for use with a specific instance of a
        Flask app. Any methods not prefixes with an underscore are candidates
        to be routed and will have routes registered when this method is
        called.

        :param app: an instance of a Flask application

        :param base_route: The base path to use for all routes registered for
                           this class. Overrides the base_route attribute if
                           it has been set.

        :param subdomain:  A subdomain that this registration should use when
                           configuring routes.

        :param route_prefix: A prefix to be applied to all routes registered
                             for this class. Precedes base_route. Overrides
                             the class' route_prefix if it has been set.
        """

        if cls is Magic:
            raise TypeError("cls must be a subclass of Magic, not Magic itself")

        if base_route:
            cls.orig_base_route = cls.base_route
            cls.base_route = base_route

        if route_prefix:
            cls.orig_route_prefix = cls.route_prefix
            cls.route_prefix = route_prefix

        if not subdomain:
            if hasattr(app, "subdomain") and app.subdomain is not None:
                subdomain = app.subdomain
            elif hasattr(cls, "subdomain"):
                subdomain = cls.subdomain

        if trailing_slash is not None:
            cls.orig_trailing_slash = cls.trailing_slash
            cls.trailing_slash = trailing_slash

        members = get_interesting_members(Magic, cls)
        special_methods = ["get", "put", "patch", "post", "delete", "index"]

        for name, value in members:
            proxy = cls.make_proxy_method(name)
            route_name = cls.build_route_name(name)
            try:
                if hasattr(value, "_rule_cache") and name in value._rule_cache:
                    for idx, cached_rule in enumerate(value._rule_cache[name]):
                        rule, options = cached_rule
                        rule = cls.build_rule(rule)
                        sub, ep, options = cls.parse_options(options)

                        if not subdomain and sub:
                            subdomain = sub

                        if ep:
                            endpoint = ep
                        elif len(value._rule_cache[name]) == 1:
                            endpoint = route_name
                        else:
                            endpoint = "%s_%d" % (route_name, idx,)

                        app.add_url_rule(rule, endpoint, proxy,
                                         subdomain=subdomain,
                                         **options)
                elif name in special_methods:
                    if name in ["get", "index"]:
                        methods = ["GET"]
                        if name == "index":
                            if hasattr(value, "_methods_cache"):
                                methods = value._methods_cache
                    else:
                        methods = [name.upper()]

                    rule = cls.build_rule("/", value)
                    if not cls.trailing_slash:
                        rule = rule.rstrip("/")
                    app.add_url_rule(rule, route_name, proxy,
                                     methods=methods,
                                     subdomain=subdomain)

                else:
                    methods = value._methods_cache \
                        if hasattr(value, "_methods_cache") \
                        else ["GET"]

                    name = utils.dasherize(name)
                    route_str = '/%s/' % name
                    if not cls.trailing_slash:
                        route_str = route_str.rstrip('/')
                    rule = cls.build_rule(route_str, value)
                    app.add_url_rule(rule, route_name, proxy,
                                     subdomain=subdomain,
                                     methods=methods)
            except DecoratorCompatibilityError:
                raise DecoratorCompatibilityError("Incompatible decorator detected on %s in class %s" % (name, cls.__name__))

        if hasattr(cls, "orig_base_route"):
            cls.base_route = cls.orig_base_route
            del cls.orig_base_route

        if hasattr(cls, "orig_route_prefix"):
            cls.route_prefix = cls.orig_route_prefix
            del cls.orig_route_prefix

        if hasattr(cls, "orig_trailing_slash"):
            cls.trailing_slash = cls.orig_trailing_slash
            del cls.orig_trailing_slash

    @classmethod
    def parse_options(cls, options):
        """Extracts subdomain and endpoint values from the options dict and returns
           them along with a new dict without those values.
        """
        options = options.copy()
        subdomain = options.pop('subdomain', None)
        endpoint = options.pop('endpoint', None)
        return subdomain, endpoint, options,

    @classmethod
    def make_proxy_method(cls, name):
        """Creates a proxy function that can be used by Flasks routing. The
        proxy instantiates the Magic subclass and calls the appropriate
        method.
        :param name: the name of the method to create a proxy for
        """

        i = cls()
        view = getattr(i, name)

        if cls.decorators:
            for decorator in cls.decorators:
                view = decorator(view)

        @functools.wraps(view)
        def proxy(**forgettable_view_args):
            # Always use the global request object's view_args, because they
            # can be modified by intervening function before an endpoint or
            # wrapper gets called. This matches Flask's behavior.
            del forgettable_view_args

            if hasattr(i, "before_request"):
                response = i.before_request(name, **request.view_args)
                if response is not None:
                    return response

            before_view_name = "before_" + name
            if hasattr(i, before_view_name):
                before_view = getattr(i, before_view_name)
                response = before_view(**request.view_args)
                if response is not None:
                    return response

            response = view(**request.view_args)

            # You can also return a dict or None, it will pass it to render
            if isinstance(response, dict) or response is None:
                response = response or {}
                if hasattr(i, "_renderer"):
                    response = i._renderer(response)
                else:
                    df_v_t = "%s/%s.html" % (cls.__name__, view.__name__)
                    response.setdefault("template_", df_v_t)
                    response = i.render_(**response)

            if not isinstance(response, Response):
                response = make_response(response)

            after_view_name = "after_" + name
            if hasattr(i, after_view_name):
                after_view = getattr(i, after_view_name)
                response = after_view(response)

            if hasattr(i, "after_request"):
                response = i.after_request(name, response)

            return response

        return proxy

    @classmethod
    def build_rule(cls, rule, method=None):
        """Creates a routing rule based on either the class name (minus the
        'View' suffix) or the defined `base_route` attribute of the class

        :param rule: the path portion that should be appended to the
                     route base

        :param method: if a method's arguments should be considered when
                       constructing the rule, provide a reference to the
                       method here. arguments named "self" will be ignored
        """

        rule_parts = []

        if cls.route_prefix:
            rule_parts.append(cls.route_prefix)

        base_route = cls.get_base_route()
        if base_route:
            rule_parts.append(base_route)

        rule_parts.append(rule)
        ignored_rule_args = ['self']
        if hasattr(cls, 'base_args'):
            ignored_rule_args += cls.base_args

        if method:
            args = get_true_argspec(method)[0]
            for arg in args:
                if arg not in ignored_rule_args:
                    rule_parts.append("<%s>" % arg)

        result = "/%s" % "/".join(rule_parts)
        return re.sub(r'(/)\1+', r'\1', result)

    @classmethod
    def get_base_route(cls):
        """Returns the route base to use for the current class."""

        if cls.base_route is not None:
            base_route = cls.base_route
            base_rule = parse_rule(base_route)
            cls.base_args = [r[2] for r in base_rule]
        else:
            if cls.__name__.endswith("View"):
                base_route = cls.__name__[:-4].lower()
            else:
                base_route = cls.__name__.lower()

        return base_route.strip("/")

    @classmethod
    def build_route_name(cls, method_name):
        """Creates a unique route name based on the combination of the class
        name with the method name.

        :param method_name: the method name to use when building a route name
        """
        return cls.__name__ + ":%s" % method_name

# MagicWand
MagicWand = Magic()

# ------------------------------------------------------------------------------


def get_interesting_members(base_class, cls):
    """Returns a list of methods that can be routed to"""

    base_members = dir(base_class)
    predicate = inspect.ismethod if _py2 else inspect.isfunction
    all_members = inspect.getmembers(cls, predicate=predicate)
    return [member for member in all_members
            if not member[0] in base_members
            and ((hasattr(member[1], "__self__") and not member[1].__self__ in inspect.getmro(cls)) if _py2 else True)
            and not member[0].startswith("_")
            and not member[0].startswith("before_")
            and not member[0].startswith("after_")]


def get_true_argspec(method):
    """Drills through layers of decorators attempting to locate the actual argspec for the method."""

    argspec = inspect.getargspec(method)
    args = argspec[0]
    if args and args[0] == 'self':
        return argspec
    if hasattr(method, '__func__'):
        method = method.__func__
    if not hasattr(method, '__closure__') or method.__closure__ is None:
        raise DecoratorCompatibilityError

    closure = method.__closure__
    for cell in closure:
        inner_method = cell.cell_contents
        if inner_method is method:
            continue
        if not inspect.isfunction(inner_method) \
            and not inspect.ismethod(inner_method):
            continue
        true_argspec = get_true_argspec(inner_method)
        if true_argspec:
            return true_argspec


class DecoratorCompatibilityError(Exception):
    pass


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

