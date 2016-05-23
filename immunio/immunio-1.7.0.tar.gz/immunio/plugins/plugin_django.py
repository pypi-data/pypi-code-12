from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from functools import (
    partial,
    wraps,
)
from hashlib import sha1
import types

from immunio.logger import log
from immunio.patcher import monkeypatch


# Set name so plugin can be enabled and disabled.
NAME = "django"


def sha1hash(value):
    """
    Return the sha1 hash of the provided value, or None if `value` is None.
    """
    if value is None:
        return None
    return sha1(value).hexdigest()


def add_hooks(run_hook, get_agent_func=None, timer=None):
    """
    Add our hooks into the django library functions.
    """
    try:
        import django
        import django.conf
    except ImportError:
        return None

    # Install a hook to capture newly created wsgi apps and wrap them.
    hook_get_wsgi_application(run_hook, get_agent_func, timer)

    # This installs all the other settings-dependent hooks as well, ensuring
    # that it does so only after settings are configured.
    hook_settings(run_hook, timer)

    # This installs informational hooks in the Django querysets.
    hook_queryset(get_agent_func, timer)
    hook_fields(get_agent_func, timer)
    hook_Q(get_agent_func, timer)

    meta = {
        "version": django.get_version(),
    }

    return meta


def hook_get_wsgi_application(run_hook, get_agent_func, timer):
    """
    Wrap the `get_wsgi_application()` function so we can wrap each WSGI
    app as it is produced. This also creates the Agent if it hasn't been
    created yet.
    """
    try:
        import django.core.wsgi
    except ImportError:
        return

    # If we don't have a `get_agent_func()` defined the app will be
    # wrapped elsewhere.
    if get_agent_func:
        @monkeypatch(django.core.wsgi, "get_wsgi_application", timer=timer,
                     report_name="plugin.django.get_wsgi_application")
        def _get_wsgi_application(orig, *args, **kwargs):
            # Get the WSGI app
            app = orig(*args, **kwargs)
            # Get or create the Immunio Agent singleton
            agent = get_agent_func()
            # Wrap the WSGI app object with Immunio.
            app = agent.wrap_wsgi_app(app)
            return app


def install_model_importing_hooks(run_hook, timer):
    """These hooks import models."""
    hook_contrib_auth(run_hook, timer)


def install_settings_dependent_hooks(run_hook, timer):
    """These hooks require settings to be configured."""
    try:
        import django
    except ImportError:
        return

    hook_http_request(run_hook, timer)
    hook_url_resolver(run_hook, timer)
    hook_session_middleware(run_hook, timer)
    hook_csrf_middleware(run_hook, timer)
    hook_response_bad_header(run_hook, timer)

    # In Django 1.7+, we should also wait to install model-importing hooks
    # until django.setup() is called. Importing models before the app-cache is
    # populated raises warnings in 1.7+ and will be an error in 1.9+.
    if hasattr(django, 'setup'):
        from django.apps import apps

        model_importing_hooks_installed = []

        if apps.ready:
            install_model_importing_hooks(run_hook, timer)
            model_importing_hooks_installed.append(True)
        else:
            original_populate = apps.populate

            @wraps(original_populate)
            def new_populate(installed_apps=None):
                original_populate(installed_apps)
                if not model_importing_hooks_installed:
                    install_model_importing_hooks(run_hook, timer)
                    model_importing_hooks_installed.append(True)

            apps.populate = new_populate
    else:
        # In earlier versions of Django, importing models early was OK.
        install_model_importing_hooks(run_hook, timer)


def hook_http_request(run_hook, timer):
    """
    Hook the Django http request to catch bad signatures when getting
    signed cookies.
    """
    try:
        from django.core.signing import BadSignature
        from django.http.request import (
            HttpRequest,
            RAISE_ERROR,
        )
    except ImportError:
        return

    @monkeypatch(HttpRequest, "get_signed_cookie", timer=timer,
                 report_name="plugin.django.get_signed_cookie")
    def _get_signed_cookie(
            orig, self, key, default=RAISE_ERROR, salt='', max_age=None):
        # Save original value of the default
        original_default = default

        try:
            # Call the original get_signed_cookie() but always ask for
            # exceptions to be raised
            return orig(self, key, default=RAISE_ERROR, salt=salt,
                        max_age=max_age)
        except (KeyError, BadSignature) as exc:
            # If we have a bad signature, run the lua hook
            if isinstance(exc, BadSignature):
                run_hook("bad_cookie", {
                    "key": key,
                    "value": self.COOKIES[key],
                    "reason": str(exc),
                })
            # If the original call specified a default,
            # return it instead of raising.
            if original_default is RAISE_ERROR:
                raise
            else:
                return original_default


def hook_url_resolver(run_hook, timer):
    """
    Hook the Django URL resolver so we know which Django view is handling each
    request.
    """
    try:
        import django.core.urlresolvers
    except ImportError:
        return

    @monkeypatch(django.core.urlresolvers.RegexURLResolver, "resolve",
                 timer=timer, report_name="plugin.django.url_resolver")
    def _resolve(orig, self, path):
        log.debug(
            "django.core.urlresolvers.RegexURLResolver.resolve(%(path)s)", {
                "path": path,
                })
        route_name = None
        try:
            result = orig(self, path)

            # Build view name from ResolverMatch
            if isinstance(result.func, basestring):
                route_name = result.func
            else:
                # Workaround for tests that might pass a partial.
                if isinstance(result.func, partial):
                    func = result.func.func
                else:
                    func = result.func

                if isinstance(result.func, types.FunctionType):
                    route_name = func.__name__
                else:
                    route_name = func.__class__.__name__ + '.__call__'

                # Prefix view name with module name
                route_name = "%s.%s" % (func.__module__, route_name)
        finally:
            # Send hook
            run_hook("framework_route", {
                "route_name": route_name,
            })
        return result


def hook_contrib_auth(run_hook, timer):
    """
    Hook the Django authentication system to detect login attempts.
    """
    try:
        import django.contrib.auth
        import django.contrib.auth.backends
        import django.contrib.auth.models
        from django.contrib.auth.middleware import AuthenticationMiddleware
    except ImportError:
        return

    def get_username(user):
        """Get a user's username.

        Compatible with both Django 1.4, and custom user models with
        USERNAME_FIELD in Django 1.5+.

        """
        try:
            return user.get_username()
        except AttributeError:
            return getattr(user, 'username', None)

    @monkeypatch("django.contrib.auth.authenticate", timer=timer,
                 report_name="plugin.django.auth.authenticate")
    def _authenticate(orig, **credentials):
        log.debug("django.contrib.auth.authenticate(%(credentials)s)", {
            "credentials": credentials,
            })

        try:
            # Django 1.5 and above use the get_user_model function.
            UserModel = django.contrib.auth.backends.get_user_model()
            username_field = UserModel.USERNAME_FIELD
        except AttributeError:
            # Django 1.4 and below use the User model.
            UserModel = django.contrib.auth.models.User
            username_field = "username"

        username = credentials.get(username_field)

        auth_data = {
            "username": username,
            "is_valid": True
            }

        user = orig(**credentials)
        if user is None:
            auth_data["is_valid"] = False
            auth_data["reason"] = "password"
            if username:
                try:
                    UserModel._default_manager.get_by_natural_key(username)
                except:
                    # Catch everything instead of just DoesNotExist.
                    auth_data["reason"] = "username"
            else:
                auth_data["reason"] = "username"

        run_hook("authenticate", auth_data)
        return user

    @monkeypatch("django.contrib.auth.login", timer=timer,
                 report_name="plugin.django.auth.login")
    def _login(orig, request, user):
        log.debug("django.contrib.auth.login(%(request)s, %(user)s)", {
            "request": request,
            "user": user,
            })

        # Logging in will change our session key. Record the old session_id
        old_session_id = request.session.session_key

        # Call login
        result = orig(request, user)

        session_accessed = request.session.accessed
        try:
            # Django login does not always set request.user; only if request
            # already had a `user` attribute. And it can be called with
            # `user=None`, in which case the user is taken from the request. So
            # we have to be able to take the user from either one, but we can
            # count on it being available from one or the other.
            actual_user = user or request.user
        finally:
            # Accessing request.user will mark the session as accessed, thus
            # triggering Vary: Cookie on the response. We need to reset this.
            request.session.accessed = session_accessed

        # Send hook
        run_hook("framework_login", {
            "user_id": actual_user.pk,
            "username": get_username(actual_user),
            # Use the SHA1 of the session_id so the VM does not have access
            # to the actual real session_id.
            "old_session_id": sha1hash(old_session_id),
            "new_session_id": sha1hash(request.session.session_key),
        })
        return result

    @monkeypatch("django.contrib.auth.logout", timer=timer,
                 report_name="plugin.django.auth.logout")
    def _logout(orig, request):
        log.debug("django.contrib.auth.logout(%(request)s)", {
            "request": request,
            })

        # Logging out will change our session key. Record the old session_id
        old_session_id = request.session.session_key
        result = orig(request)
        # Send hook
        run_hook("framework_logout", {
            # Use the SHA1 of the session_id so the VM does not have access
            # to the actual real session_id.
            "old_session_id": sha1hash(old_session_id),
            "new_session_id": sha1hash(request.session.session_key),
        })
        return result

    @monkeypatch("django.contrib.auth.get_user", timer=timer,
                 report_name="plugin.django.auth.get_user")
    def _get_user(orig, request):
        log.debug("django.contrib.auth.get_user(%(request)s)", {
            "request": request,
            })

        user = orig(request)

        # Only send hook if user is not anonymous, otherwise an user_id
        # and username are None resulting in an empty framework_user dict.
        if not user.is_anonymous():
            run_hook("framework_user", {
                "user_id": user.pk,
                "username": get_username(user),
            })

        return user

    @monkeypatch(AuthenticationMiddleware, "process_request", timer=timer,
                 report_name="plugin.django.auth.process_request")
    def _process_request(orig, self, request):
        """
        We don't actually send any hooks from here - we just need to access
        `request.user` to activate the lazy object to trigger the
        `get_user()` hook above.
        """
        log.debug("AuthenticationMiddleware.process_request(%(request)s)", {
            "request": request,
            })

        result = orig(self, request)

        # If no session store is used, there may be no `request.session`.
        if hasattr(request, "session") and request.session is not None:
            session_accessed = request.session.accessed

        try:
            # Don't do anything with result, just trigger the LazyObject
            request.user
        finally:
            # Accessing request.user will mark the session as accessed, thus
            # triggering Vary: Cookie on the response. We need to reset this.
            if hasattr(request, "session") and request.session is not None:
                request.session.accessed = session_accessed

        return result


def hook_session_middleware(run_hook, timer):
    """
    Hook the session middleware system to determine the active session for each
    request and to detect potential session tampering.
    """
    try:
        from django.contrib.sessions.middleware import SessionMiddleware
    except ImportError:
        return

    @monkeypatch(SessionMiddleware, "process_request", timer=timer,
                 report_name="plugin.django.session.process_request")
    def _process_request(orig, self, request):
        log.debug("SessionMiddleware.process_request(%(request)s)", {
            "request": request,
            })

        result = orig(self, request)
        try:
            # Get session_key from session
            session_key = request.session.session_key
        except AttributeError:
            session_key = None

        # Send hook
        run_hook("framework_session", {
            # Use the SHA1 of the session_id so the VM does not have access
            # to the actual real session_id.
            "session_id": sha1hash(session_key),
        })
        return result


def hook_csrf_middleware(run_hook, timer):
    """
    Hook the CSRF middleware system to determine the CSRF status for each
    request. This also works with the `csrf_protect` decorator since it
    just uses the middleware.
    """
    try:
        from django.middleware.csrf import CsrfViewMiddleware
    except ImportError:
        return

    @monkeypatch(CsrfViewMiddleware, "_accept", timer=timer,
                 report_name="plugin.django.csrf.accept")
    def _accept(orig, self, request):
        log.debug("CsrfViewMiddleware._accept(%(request)s)", {
            "request": request,
            })

        # Send hook
        run_hook("framework_csrf_check", {
            "valid": True,
        })
        return orig(self, request)

    @monkeypatch(CsrfViewMiddleware, "_reject", timer=timer,
                 report_name="plugin.django.csrf.reject")
    def _reject(orig, self, request, reason):
        if isinstance(reason, unicode):
            reason = reason.encode("utf-8")

        log.debug("CsrfViewMiddleware._reject(%(request)s, %(reason)s)", {
            "request": request,
            "reason": reason,
            })

        # Send hook
        run_hook("framework_csrf_check", {
            "valid": False,
            "reason": reason,
        })
        return orig(self, request, reason)


def hook_settings(run_hook, timer):
    try:
        import django.conf
    except ImportError:
        return

    settings_dependent_hooks_installed = []

    # Hook the settings module
    settings = django.conf.settings

    # If settings are already configured, install setting-dependent hooks now
    if settings.configured:
        install_settings_dependent_hooks(run_hook, timer)
        settings_dependent_hooks_installed.append(True)

    # Normally, the initial settings configuration looks like a bunch of
    # individual changes. Share them up so we get a single hook called.
    shared = {
        "settings": {},
        "collecting": False,
        }

    # Hook the settings object to catch attribute changes
    orig_set_attr = django.conf.BaseSettings.__setattr__

    def new_set_attr(bound_self, name, value):
        log.debug(
            "django.conf.BaseSettings.__setattr__(%(name)s, %(value)s)", {
                "name": name,
                "value": value,
                })
        if shared["collecting"]:
            # Don't fire change hook, collect instead
            shared["settings"][name] = value
        else:
            # Not collecting, fire the change hook
            run_hook("change_setting", {"name": name, "value": value})

        return orig_set_attr(bound_self, name, value)
    setattr(django.conf.BaseSettings, "__setattr__", new_set_attr)

    orig_setup = settings._setup

    def new_setup(*args, **kwargs):
        log.debug(
            "settings._setup(%(args)s, %(kwargs)s)", {
                "args": args,
                "kwargs": kwargs,
                })
        # Set up collecting
        shared["settings"] = {}
        shared["collecting"] = True
        try:
            orig_setup(*args, **kwargs)
            run_hook("load_settings", {"settings": shared["settings"]})
        finally:
            shared["settings"] = {}
            shared["collecting"] = False
        if not settings_dependent_hooks_installed:
            install_settings_dependent_hooks(run_hook, timer)
            settings_dependent_hooks_installed.append(True)
    settings.__dict__["_setup"] = new_setup

    orig_configure = settings.configure

    def new_configure(*args, **kwargs):
        log.debug(
            "settings.configure(%(args)s, %(kwargs)s)", {
                "args": args,
                "kwargs": kwargs,
                })
        # Set up collecting
        shared["settings"] = {}
        shared["collecting"] = True
        try:
            orig_configure(*args, **kwargs)
            run_hook("configure_settings", {"settings": shared["settings"]})
        finally:
            shared["settings"] = {}
            shared["collecting"] = False
        if not settings_dependent_hooks_installed:
            install_settings_dependent_hooks(run_hook, timer)
            settings_dependent_hooks_installed.append(True)
    settings.__dict__["configure"] = new_configure


def hook_response_bad_header(run_hook, timer):
    """
    Hook the Django exception thrown from Response when headers are invalid.
    """
    try:
        from django.http.response import HttpResponseBase, BadHeaderError
    except ImportError:
        try:
            # django 1.4 doesn't have django.http.response
            from django.http import HttpResponse as HttpResponseBase
            from django.http import BadHeaderError
        except ImportError:
            # No django
            return

    @monkeypatch(HttpResponseBase, "__setitem__", timer=timer,
                 report_name="plugin.django.bad_header.setitem")
    def __setitem__(orig, self, header, value):
        log.debug("HttpResponseBase.__setitem__(%(header)s, %(value)s)", {
            "header": header,
            "value": value,
            })
        try:
            return orig(self, header, value)
        except (BadHeaderError, UnicodeError) as exc:
            # Send hook
            run_hook("framework_bad_response_header", {
                "header": header,
                "value": value,
                "reason": str(exc),
            })
            raise  # re-raise exception back to application after we're done


def hook_queryset(get_agent_func, timer):
    """
    Hook the Django Queryset functions to track how the db query
    was created.

    See: django/db/models/query.py and make sure the method list
    stays up to date.
    """

    try:
        from django.db.models.query import QuerySet
        from django.db.models import Q
    except ImportError:
        log.debug("No Django QuerySet found")
        return

    to_patch = [QuerySet]
    while to_patch:
        klass = to_patch.pop(0)
        to_patch.extend(klass.__subclasses__())
        log.debug("Patching %s", klass.__name__)
        _hook_queryset_class(get_agent_func, timer, klass, Q)


def _hook_queryset_class(get_agent_func, timer, klass, Q):

    def arg_to_str(arg):
        if isinstance(arg, Q):
            return arg._immunio_str()
        else:
            return str(type(arg))

    def make_method_sig(method_name, args, kwargs):
        args_sig = ",".join(arg_to_str(arg) for arg in args)
        kwargs_sig = ",".join(["{0}:{1}".format(key, type(value)) for key, value
                           in kwargs.iteritems()])
        param_sig = ",".join(filter(None, [args_sig, kwargs_sig]))
        method_sig = "{0}({1})".format(method_name, param_sig)
        return method_sig

    # Setup new QuerySets:
    if "__init__" in klass.__dict__:
        @monkeypatch(klass, "__init__", timer=timer,
                     report_name="plugin.django.sqli.queryset.init")
        def __init__(orig, self, *args, **kwargs):
            log.debug("QuerySet.__init__()")

            self._immunio_path = []
            model = None
            if len(args):
                model = args[0]
            elif 'model' in kwargs:
                model = kwargs['model']

            if model:
                try:
                    model_str = model._meta.db_table
                except AttributeError:
                    try:
                        model_str = model._meta.model_name
                    except AttributeError:
                        model_str = "Unknown"

                self._immunio_path.append("{0}.__init__({1})".format(
                    self.__class__.__name__, model_str))

            # If query and using still results in F+ they may have to
            # be added here as well. Instead of adding `using` directly
            # it would probably make sense to use the `db` property after
            # the object is created.
            return orig(self, *args, **kwargs)

    # Handle copies (Django does this a lot):
    if "_clone" in klass.__dict__:
        @monkeypatch(klass, "_clone", timer=timer,
                     report_name="plugin.django.sqli.queryset.clone")
        def _clone(orig, self, *args, **kwargs):
            log.debug("QuerySet._clone()")

            clone = orig(self, *args, **kwargs)
            if not hasattr(self, "_immunio_path"):
                self._immunio_path = []
            clone._immunio_path.extend(self._immunio_path[:])
            return clone

    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################
    if "iterator" in klass.__dict__:

        @monkeypatch(klass, "iterator", timer=timer,
                     report_name="plugin.django.sqli.queryset.iterator")
        def _iterator(orig, self, *args, **kwargs):
            log.debug("QuerySet.iterator()")

            if get_agent_func:
                agent = get_agent_func()
                with agent.property_set("QuerySet_calls",
                                        self._immunio_path):
                    generator = orig(self, *args, **kwargs)
                    if not isinstance(generator, types.GeneratorType):
                        generator = (v for v in generator)

                # Only set the property while actually retrieving the values
                # StopIteration will escape this loop
                while True:
                    with agent.property_set("QuerySet_calls",
                                            self._immunio_path):
                        next_value = generator.next()
                    yield next_value
            else:
                for next_value in orig(self, *args, **kwargs):
                    yield next_value

    db_methods = [
            "aggregate",
            "count",
            "get",
            "create",
            "_populate_pk_values",
            "bulk_create",
            "get_or_create",
            "update_or_create",
            "_create_object_from_params",
            "_extract_model_params",
            "_earliest_or_latest",
            "earliest",
            "latest",
            "first",
            "last",
            "in_bulk",
            "delete",
            "_raw_delete",
            "update",
            "exists",
            "_prefetch_related_objects",
    ]
    def patch_qs_db(method_name):
        @monkeypatch(klass, method_name, timer=timer,
                     report_name="plugin.django.sqli.queryset.%s" % method_name)
        def _call_with_path(orig, self, *args, **kwargs):
            log.debug("QuerySet.%s", method_name)

            # These calls do not return a new QS, so instead just
            # append the method signature for the length of the call

            if get_agent_func:
                method_sig = make_method_sig(method_name, args, kwargs)
                self._immunio_path.append(method_sig)
                try:
                    agent = get_agent_func()
                    with agent.property_set("QuerySet_calls",
                                            self._immunio_path):
                        return orig(self, *args, **kwargs)
                finally:
                    self._immunio_path.pop()

            else:
                return orig(self, *args, **kwargs)

    for method in db_methods:
        if not method in klass.__dict__:
            continue
        try:
            patch_qs_db(method)
        except AttributeError:
            log.debug("Unable to patch Django's %s %s", klass.__name__, method)

    # _update takes a list of fields, and must be expanded to account
    # for NULL values inside:
    if "_update" in klass.__dict__:
        @monkeypatch(klass, "_update", timer=timer,
                     report_name="plugin.django.sqli.queryset._update")
        def _call_with_path_expand(orig, self, values):
            log.debug("QuerySet._update")

            if get_agent_func:
                if values:
                    real_values = [value for (_field, _model, value) in values]
                else:
                    real_values = []
                method_sig = make_method_sig("_update", real_values, {})
                self._immunio_path.append(method_sig)
                try:
                    agent = get_agent_func()
                    with agent.property_set("QuerySet_calls",
                                            self._immunio_path):
                        return orig(self, values)
                finally:
                    self._immunio_path.pop()

            else:
                return orig(self, values)


    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################
    alter_methods = [
            "all",
            "filter",
            "exclude",
            "_filter_or_exclude",
            "complex_filter",
            "select_for_update",
            "select_related",
            "prefetch_related",
            "annotate",
            "order_by",
            "distinct",
            "extra",
            "reverse",
            "defer",
            "only",
            "using",
    ]

    def patch_qs_alter(method_name):
        @monkeypatch(klass, method_name, timer=timer,
                     report_name="plugin.django.sqli.queryset.%s" % method_name)
        def _log_call(orig, self, *args, **kwargs):
            log.debug("QuerySet.%s", method_name)
            qs = orig(self, *args, **kwargs)

            method_sig = make_method_sig(method_name, args, kwargs)
            qs._immunio_path.append(method_sig)
            return qs

    for method in alter_methods:
        if method not in klass.__dict__:
            continue
        try:
            patch_qs_alter(method)
        except AttributeError:
            log.debug("Unable to patch Django's %s %s", klass.__name__, method)

    ########################
    # PYTHON MAGIC METHODS #
    ########################
    if "__getitem__" in klass.__dict__:
        @monkeypatch(klass, "__getitem__", timer=timer,
                     report_name="plugin.django.sqli.queryset.__getitem__")
        def _log_limits(orig, self, k, **kwargs):
            log.debug("Queryset.__getitem__")

            if not get_agent_func:
                return orig(self, k)
            agent = get_agent_func()

            # Let Django throw it's error:
            if not isinstance(k, (slice, int, long)):
                return orig(self, k)

            if isinstance(k, slice):
                stop = False
                if k.stop:
                    stop = True
                start = False
                if k.start:
                    start = True
            elif k:
                start = True
                stop = True
            else:  # k == 0
                start = False
                stop = True

            get_path = "__getitem__({0},{1})".format(start, stop)
            with agent.property_set("QuerySet_calls", (self._immunio_path +
                                                       [get_path])):
                result = orig(self, k)

            # Anything that's a QS will have this:
            if hasattr(result, "_immunio_path"):
                result._immunio_path.append(get_path)
            return result


def hook_fields(get_agent_func, timer):
    """
    Hook the locations needed to track field types where the SQL can
    differ for the same call.

    For example:
      model.num_field = 100
      model.num_field = None
    These will generate either '= %s', or '= NULL'.
    """

    from django.db.models.signals import pre_save, post_save
    from django.dispatch import receiver

    # If we're seeing differences in m2m calls consider monitoring the
    # m2m_changed signal.

    def _format_fields(instance, fields):
        field_types = []
        for field in fields:
            if hasattr(field, 'attname'):
                try:
                    vtype = type(getattr(instance, field.attname))
                except:
                    # In cases where the type points to an missing object
                    vtype = type(None)
                field_types.append("{0}:{1}".format(field.attname, vtype))
        return "|".join(field_types)

    @receiver(pre_save, weak=False)
    def _set_fields(sender, instance, raw, *args, **kwargs):
        """ In Django > 1.5 there is a fourth arg, 'update_fields', that can
        be used to limit the signature to only changed fields.
        """
        if args:
            update_fields = args[0]
        else:
            update_fields = kwargs.get('update_fields')

        if not update_fields:
            field_sig = _format_fields(instance, instance._meta.fields)
        else:
            fields = [instance._meta.get_field(name) for name in
                      update_fields]
            field_sig = _format_fields(instance, fields)

        if get_agent_func:
            agent = get_agent_func()
            cm = agent.property_set("FieldSig", field_sig)
            instance._immunio_exit = cm.__exit__

    @receiver(post_save, weak=False)
    def _unset_fields(sender, instance, *args, **kwargs):
        if hasattr(instance, '_immunio_exit'):
            instance._immunio_exit(None, None, None)


def hook_Q(get_agent_func, timer):
    """
    Hook django's tree.Node to allow us to str() the results to include
    the fields but not their values.

    Currently str(Q(year__gt, 1900)) == (AND: ('year__gt', 1900))

    Instead we need a way to print them out so the end up as:

    (AND: ('year__gt'))
    """

    import django.db.models
    from django.db.models import Q

    def _immunio_str(self):
        children_str = []
        for child in self.children:
            if isinstance(child, django.db.models.Q):
                children_str.append(child._immunio_str())
            elif isinstance(child, tuple):
                k, v = child
                children_str.append("({0}, {1})".format(k, type(v)))
            else:
                children_str.append(str(child))
        if self.negated:
            return '(NOT: ({0}: {1}))'.format(self.connector,
                                            ", ".join(children_str))
        else:
            return '({0}: {1}'.format(self.connector, ", ".join(children_str))
    Q._immunio_str = _immunio_str
