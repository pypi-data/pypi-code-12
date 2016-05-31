# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.core.management.base import OutputWrapper
from django.db import connection
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper
from django.template.defaultfilters import filesizeformat, pluralize
from django.views.static import serve as static_serve
import datetime
import logging
import sys
import threading
import time


"""
A collection of tools for simple profiling of blocks of code, entire methods or requests.
Measures elapsed time and queries performed within the block,
and outputs to the Django built-in logging system.
Messages are issued to the 'inoa.profiling' logger with the Debug level.

If you want to send the profiler output to stdout, define a suitable logger/handler combination
in your project settings. A minimal setup would be:

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'profiling': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

"""

profiler_enabled = settings.DEBUG or getattr(settings, 'ENABLE_PROFILER_IN_PRODUCTION', False)
profiling_logger = logging.getLogger('inoa.profiling')
middleware_logger = logging.getLogger('inoa.profiling.SimpleProfilerMiddleware')
bolt_easter_egg = getattr(settings, 'PROFILER_BOLT_EASTER_EGG', False)
force_sql_logging = getattr(settings, 'SIMPLE_PROFILER_FORCE_SQL_LOGGING', False)

MIDDLEWARE_LOGGER_MESSAGE_LEVEL = 75


def method_profiler(method):
    """
    Use as a decorator in any method. Usage:

    @method_profiler
    def my_method(arg1, arg2):
        ... # Do stuff you want to benchmark.
    """
    if not profiler_enabled:
        return method
    def wrapper(*args, **kwargs):
        p = Profiler("%s.%s" % (method.__module__, method.__name__))
        ret = method(*args, **kwargs)
        p.stop()
        return ret
    wrapper.__name = method.__name__
    wrapper.__module__ = method.__module__
    return wrapper


class SimpleProfilerMiddleware:
    """
    Enable this middleware to attach a profiler to each request and emit log messages
    with INFO level to the 'inoa.profiling.SimpleProfilerMiddleware' logger.
    For better results, ensure this is the first middleware in MIDDLEWARE_CLASSES.

    Query counting is disabled by default when DEBUG is False. To enable it,
    set SIMPLE_PROFILER_FORCE_SQL_LOGGING = True in the settings.
    """

    def process_request(self, request):
        if request.path_info == '/favicon.ico' or not profiler_enabled:
            request.simple_profiler = None
        else:
            request.simple_profiler = Profiler(name='request', logger=None)
            if force_sql_logging:
                Profiler.force_query_logging()

    def process_view(self, request, view, args, kwargs):
        if view == staticfiles_serve or view == static_serve:
            request.simple_profiler = None
        elif getattr(request, 'simple_profiler', None):
            request.simple_profiler.name = "%s.%s" % (view.__module__, view.__name__)

    def process_response(self, request, response):
        if not hasattr(request, 'session'):
            return response
        try:
            messages = request.session.pop('simple_profiler_messages', [])
        except:
            messages = []

        if getattr(request, 'simple_profiler', None):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            size = filesizeformat(len(response.content)) if not response.streaming else "[stream]"
            _, dt, dq = request.simple_profiler.stop()
            dqp = pluralize(dq, "query,queries")
            msg = u"[%s] %s %s -> [%s] %s in %.03fs (%s %s) from %s" % (
                now, request.method, request.path_info, response.status_code,
                size, dt, dq, dqp, request.simple_profiler.name)
            middleware_logger.info(msg)
            messages.append(msg)

        if messages and not response.streaming and response.content.rstrip()[-7:] == '</html>':
            content = response.content
            pos = content.rfind('</body>')
            js_msg = u"""
                <script type="text/javascript">
                function consoleLogProfiling(text) {
                    if (window.console) {
                        if (window.console.cd) // IE
                            window.console.info(text);
                        else // Chrome
                            window.console.info("%c" + text, "color: green");
                    }
                }
            """.strip()
            for msg in messages:
                js_msg += u'\nconsoleLogProfiling("%s");' % msg
            js_msg += u'\n</script>'
            response.content = '%s%s%s' % (content[:pos], js_msg.encode('utf-8'), content[pos:])
        else:
            try:
                request.session['simple_profiler_messages'] = messages
            except:
                pass

        return response


class Profiler(object):
    """
    Allows profiling of sections of code within a method. Usage:

    def my_method(arg1, arg2):
        ... # Do stuff you don't care about.
        profiler = Profiler()                 # Begins profiling. Note: accepts an optional name parameter.
        ... # Do stuff you want to benchmark separately.
        profiler.checkpoint()                 # Outputs partial time and queries.
        ... # Do more stuff you want to benchmark separately.
        profiler.checkpoint('Foo'd the bar')  # Outputs partial time and queries.
        ... # Do a little bit more of stuff.
        profiler.stop()                       # Outputs total time and queries.
        ... # Do stuff you don't care about.

    You can obtain a reference to the latest instantiated profiler with Profiler.get_latest().
    It creates a new profiler automatically if none exists. This is method is thread-safe.

    Use stdout=True to easily force output to stdout without having to configure loggers or streams.
    Use fake=True to create a disabled profiler (accepting the same methods, but without producing any effects/outputs).
    """
    local_store = threading.local()

    @classmethod
    def get_latest(cls):
        return getattr(cls.local_store, 'latest_instance', cls())

    def __init__(self, name=None, logger=profiling_logger, stream=None, stdout=False, stream_prefix=None, fake=False):
        self.disabled = not profiler_enabled or fake
        if self.disabled:
            return
        self.name = name or ("profiler %s" % id(self))
        self.logger = logger
        if stream:
            self.stream = stream
        elif stdout:
            self.stream = OutputWrapper(sys.stdout)
        else:
            self.stream = None
        self.stream_prefix = stream_prefix or u""
        self.start()

    def start(self):
        if self.disabled:
            return
        self.t0 = time.time()
        self.q0 = len(connection.queries)  # @UndefinedVariable
        self.t1, self.q1 = self.t0, self.q0
        self.count = 0
        self.__class__.latest_instance = self

    def log(self, msg, ending=None):
        if self.disabled:
            return
        if self.logger:
            self.logger.debug(msg)
        if self.stream:
            self.stream.write(self.stream_prefix + msg, ending=ending)
        return msg

    def checkpoint(self, name=None, ending=None):
        if self.disabled:
            return
        t2 = time.time()
        q2 = len(connection.queries)  # @UndefinedVariable
        self.count += 1
        name = name or self.count
        dt = t2 - self.t1
        dq = q2 - self.q1
        dqt = sum((float(q['time']) for q in connection.queries[-dq:]), 0.0) if dq else 0.0
        if bolt_easter_egg:
            msg = "Bolt would have run %.01f meters during partial %s, with %s queries (%.04fs in sql)." \
                  % (dt * 10.4389, name, dq, dqt)
        else:
            msg = "Partial %s in %.04f seconds with %s queries (%.04fs in sql)." % (name, dt, dq, dqt)

        self.t1, self.q1 = t2, q2
        self.__class__.latest_instance = self
        if self.logger:
            self.logger.debug(msg)
        if self.stream:
            self.stream.write(self.stream_prefix + msg, ending=ending)
        return (msg, dt, dq)

    def stop(self, ending=None):
        if self.disabled:
            return
        t2 = time.time()
        q2 = len(connection.queries)  # @UndefinedVariable
        dt = t2 - self.t0
        dq = q2 - self.q0
        dqt = sum((float(q['time']) for q in connection.queries[-dq:]), 0.0) if dq else 0.0
        if bolt_easter_egg:
            msg = "Bolt would have run %.01f meters during execution of %s, "\
                  "with %s queries (%.04fs in sql)." % (dt * 10.4389, self.name, dq, dqt)
        else:
            msg = "Executed %s in %.04f seconds with %s queries (%.04fs in sql)." % (self.name, dt, dq, dqt)
        if self.logger:
            self.logger.debug(msg)
        if self.stream:
            self.stream.write(self.stream_prefix + msg, ending=ending)
        return (msg, dt, dq)

    @classmethod
    def force_query_logging(cls):
        # Force a minimal version of the debug cursor to be used, so SQL queries will be counted.
        BaseDatabaseWrapper.cursor = get_cursor

def get_cursor(_self):
    _self.validate_thread_sharing()
    if (_self.use_debug_cursor or
        (_self.use_debug_cursor is None and settings.DEBUG)):
        cursor = _self.make_debug_cursor(_self._cursor())
    else:
        cursor = CountingCursorWrapper(_self._cursor(), _self)
    return cursor


class CountingCursorWrapper(CursorWrapper):
    def execute(self, sql, params=None):
        self.db.validate_no_broken_transaction()
        self.db.set_dirty()
        try:
            with self.db.wrap_database_errors:
                if params is None:
                    return self.cursor.execute(sql)
                else:
                    return self.cursor.execute(sql, params)
        finally:
            self.db.queries.append({
                'sql': "",
                'time': "",
            })

    def executemany(self, sql, param_list):
        self.db.validate_no_broken_transaction()
        self.db.set_dirty()
        try:
            with self.db.wrap_database_errors:
                return self.cursor.executemany(sql, param_list)
        finally:
            self.db.queries.append({
                'sql': "",
                'time': "",
            })
