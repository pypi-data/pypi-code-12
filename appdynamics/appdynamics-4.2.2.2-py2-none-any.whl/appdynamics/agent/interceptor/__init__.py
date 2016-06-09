# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors hook into imports to modify third-party module behavior.

"""

import sys

# These definitions must come before the subsequent imports to avoid a circular reference.
URL_PROPERTY_MAX_LEN = 100
HOST_PROPERTY_MAX_LEN = 50
DB_NAME_PROPERTY_MAX_LEN = 50
VENDOR_PROPERTY_MAX_LEN = 50

from . import cache, frameworks, http, logging, mongodb, sql


BT_INTERCEPTORS = (
    # Entry points
    ('flask', frameworks.intercept_flask),
    ('django.core.handlers.wsgi', frameworks.intercept_django_wsgi_handler),
    ('django.core.handlers.base', frameworks.intercept_django_base_handler),
    ('cherrypy', frameworks.intercept_cherrypy),

    # HTTP exit calls
    ('httplib', http.intercept_httplib),
    ('urllib3', http.intercept_urllib3),
    ('requests', http.intercept_requests),
    ('boto.https_connection', http.intercept_boto),

    # Old-style SQL exit calls
    ('psycopg2', sql.psycopg2.intercept_psycopg2),

    # SQL exit calls
    ('pymysql.connections', sql.pymysql.intercept_pymysql_connections),
    ('mysql.connector.connection', sql.mysql_connector.intercept_mysql_connector_connection),
    ('MySQLdb.connections', sql.mysqldb.intercept_MySQLdb_connection),

    # Caches
    ('redis.connection', cache.intercept_redis),
    ('memcache', cache.intercept_memcache),

    # Logging
    ('logging', logging.intercept_logging),

    # MongoDB
    ('pymongo', mongodb.intercept_pymongo),
)


def add_hook(agent):
    """Add the module interceptor hook for AppDynamics, if it's not already registered.

    """

    interceptor = ModuleInterceptor(agent)
    sys.meta_path.append(interceptor)
    return interceptor


class ModuleInterceptor(object):
    """Intercepts finding and loading modules in order to monkey patch them on load.

    """

    def __init__(self, agent):
        super(ModuleInterceptor, self).__init__()
        self.agent = agent
        self.module_hooks = {}
        self.intercepted_modules = set()

    def find_module(self, full_name, path=None):
        if full_name in self.module_hooks:
            return self
        return None

    def load_module(self, name):
        # Remove the module from the list of hooks so that we never see it again.
        hooks = self.module_hooks.pop(name, [])

        if name in sys.modules:
            # Already been loaded. Return it as is.
            return sys.modules[name]

        self.agent.logger.debug('Intercepting import %s', name)

        __import__(name)  # __import__('a.b.c') returns <module a>, not <module a.b.c>
        module = sys.modules[name]  # ...so get <module a.b.c> from sys.modules

        self._intercept_module(module, hooks)
        return module

    def call_on_import(self, module_name, cb):
        if module_name in sys.modules:
            self._intercept_module(sys.modules[module_name], [cb])
        else:
            self.module_hooks.setdefault(module_name, [])
            self.module_hooks[module_name].append(cb)

    def _intercept_module(self, module, hooks):
        try:
            for hook in hooks:
                self.agent.logger.debug('Running %s hook %r', module.__name__, hook)
                hook(self.agent, module)
            self.intercepted_modules.add(module)
        except:
            self.agent.logger.exception('Exception in %s hook.', module.__name__)

            # Re-import to ensure the module hasn't been partially patched.
            self.agent.logger.debug('Re-importing %s after error in module hook', module.__name__)
            reload(module)
