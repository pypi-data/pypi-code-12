"""
    flask.ext.autofixture
    ---------------
    This extension provides automatic recording of JSON fixtures for Flask
    right from your test suite.

    :copyright: (c) 2016 by Janusch Jacoby.
    :license: MIT/X11, see LICENSE for more details.
"""
import warnings
from flask import request, current_app, has_request_context, has_app_context, g
from functools import wraps
from .fixture import Fixture
from .storage import FileStorage, RouteLayout, RequestMethodLayout

__all__ = ('AutoFixture', 'autofixture', 'FileStorage', 'RouteLayout',
           'RequestMethodLayout')
__ext_name__ = 'autofixture'


class autofixture(object):
    """A decorator for usage in test methods to specify a descriptive
    name for the generated fixture.

    Example usage:

        @autofixture("missing_email")
        def test_missing_email_returns_bad_request(self):
            response = self.client.post(
                url_for('api.new_user'),
                data=json.dumps({'name': 'john'}))
            self.assertTrue(response.status_code == 400)

    When performing multiple request in a single test method, please
    note that decorators need to be applied in the reverse order.

    :param name: the name of the fixture to be pushed onto the stack
    """

    def __init__(self, name):
        self.name = name

    def __call__(self, func):
        @wraps(func)
        def _decorated(_self, *args, **kwargs):
            stack = None
            if not hasattr(_self, __ext_name__):
                warnings.warn("self." + __ext_name__ + " must be available" +
                              "on the test case")
            else:
                # Save name on stack
                stack = getattr(_self, __ext_name__)
                stack.push_name(self.name)
            # Execute test method
            func(_self, *args, **kwargs)
            # Cleanup stack after test method
            if stack:
                stack.clear_names()

        return _decorated


class AutoFixture(object):
    """
    A wrapper around the application for which to automatically generate
    fixtures by recording the incoming requests and outgoing responses.
    Once the application context is torn down, the recorded fixtures are
    flushed from the cache and persisted by the given :class:`Storage`
    in a fixture directory within the instance folder. The structure of
    the fixture directory is determined by the given :class:`StorageLayout`.

    To get started, you wrap your :class:`Flask` application under test
    in the setup method of your testing framework like this::

        self.app = create_app('testing')
        self.autofixture = AutoFixture(self.app)

    Alternatively, you can use :meth:`init_app` to set the Flask application
    after it has been constructed.

    :param app: :class:`Flask` application under test
    :param fixture_directory: the name of the fixture directory to be generated
    :param fixture_dirpath: the path of the fixture directory's parent folder
    :param storage_class: the :class:`Storage` to which the cache is flushed
    :param storage_layout: the :class:`StorageLayout` for the fixture directory
    """

    def __init__(self, app=None,
                 fixture_dirname=__ext_name__,
                 fixture_dirpath=None,
                 storage_class=FileStorage,
                 storage_layout=RequestMethodLayout):
        self.fixture_dirname = fixture_dirname
        self.fixture_dirpath = fixture_dirpath
        self.storage_layout = storage_layout
        self.storage_class = storage_class
        self._app = app
        self._name_stack = []

        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('RECORD_REQUESTS_ENABLED', True)

        # Setup persistent storage
        self.storage = self.storage_class(self.storage_layout,
                                          self.fixture_dirname,
                                          self.fixture_path)

        # Setup fixture cache
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        if __ext_name__ not in app.extensions:
            app.extensions[__ext_name__] = []

        if app.config['RECORD_REQUESTS_ENABLED']:
            # Register hooks
            app.after_request(self._per_request_callback)
            app.teardown_appcontext(self._flush_fixtures)

    @property
    def app(self):
        if self._app is not None:  # pragma: no cover
            return self._app

        return current_app

    @property
    def fixture_path(self):
        """The path of the parent folder containing the fixture directory.
        By default, the fixture directory is generated in the instance folder.
        :return:
        """
        if self.fixture_dirpath:
            return self.fixture_dirpath
        return self.app.instance_path

    @property
    def cache(self):
        return self.app.extensions[__ext_name__]

    @cache.setter
    def cache(self, value):
        self.app.extensions[__ext_name__] = value

    def push_name(self, name):
        self._name_stack.append(name)

    def pop_name(self):
        return self._name_stack.pop()

    def clear_names(self):
        self._name_stack = []

    def _per_request_callback(self, response):
        """The after_request function of :class:`Flask` is triggered for all
        requests. We want to hook into one specific request.

        For further info:
        http://flask.pocoo.org/snippets/53/

        :param response: the :class:`Response` to generate fixtures for
        :return:
        """
        if not hasattr(g, 'call_after_request'):
            g.call_after_request = self._extract_fixtures
            response = g.call_after_request(response)
        return response

    def _extract_fixtures(self, response):
        if not has_request_context:
            return
        try:
            if len(self._name_stack):
                fixture_name = self.pop_name()
            else:
                fixture_name = None

            # Create response fixture
            fixture = Fixture.from_response(self.app, response,
                                            name=fixture_name)
            self.cache.append(fixture)

            # Create request fixture if required
            if request.data:
                fixture = Fixture.from_request(self.app, request,
                                               name=fixture_name)
                self.cache.append(fixture)
        except TypeError:  # pragma: no cover
            warnings.warn("Could not create fixture for unsupported mime type")

        return response

    def _flush_fixtures(self, exception):
        if not has_app_context:
            return

        for fixture in self.cache:
            self.storage.store_fixture(fixture)

        self.cache = []
