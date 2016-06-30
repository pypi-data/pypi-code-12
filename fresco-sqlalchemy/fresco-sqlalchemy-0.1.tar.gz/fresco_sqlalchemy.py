# Copyright 2013 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from functools import wraps
from random import random
from time import sleep
import logging

from fresco import context, Response
from fresco.util.wsgi import ClosingIterator
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, DBAPIError

ustr = type(u'')

__version__ = '0.1'

logger = logging.getLogger(__name__)

#: For autocommit/autoretry, which errors to retry the transaction on
retryable_errors = (IntegrityError,)


class SQLAlchemy(object):
    """
    A manager for sqlalchemy sessions, bound to and configured by a fresco app.
    """

    #: Registry of active instances
    registry = {}

    sessions = None
    default_session = None

    #: The key in app.options that defines database connections
    options_key = 'SQLALCHEMY'

    #: The key in the WSGI environ used to reference sqlalchemy sessions
    environ_key = 'fresco.sqlalchemy'

    #: The key in fresco.context used to reference sqlalchemy sessions
    context_key = 'sqlalchemy'

    #: The sqlalchemy sessionmaker function. Change the behaviour of
    #: sessionmaker by overriding this
    sessionmaker = sessionmaker

    def __init__(self, app=None, databases=None, options_key=None,
                 environ_key=None, context_key=None, sessionmaker=None,
                 **kwargs):

        databases = databases or {}
        self.sessionmakers = {}
        self.urls = {}
        self.environ_key = environ_key or self.environ_key
        self.context_key = context_key or self.context_key
        self.options_key = options_key or self.options_key
        self.sessionmaker = sessionmaker or self.sessionmaker

        if app is not None:
            self.init_app(app, databases, **kwargs)
        else:
            self.init_engines(databases, **kwargs)

    def init_engines(self, databases, **kwargs):
        """
        Initialize SQLAlchemy engines and sessionmakers

        :param databases: a mapping of names to database urls
        :param kwargs: kwargs are passed trhough to create_engine, making it
                       possible to specify engine options such as ``echo=True``

        """
        for k, v in databases.items():
            self.urls[k] = v
            self.sessionmakers[k] = self.sessionmaker(
                                        bind=create_engine(v, **kwargs))

        if 'default' not in self.sessionmakers:
            if len(self.sessionmakers) == 1:
                self.sessionmakers['default'] = \
                        next(self.sessionmakers.values())

    def init_app(self, app, databases=None, **kwargs):
        """
        Initialize a :class:`fresco.core.FrescoApp` for use with
        fresco_sqlalchemy
        """
        self.registry[app] = self
        if not databases:
            databases = app.options.get(self.options_key, {})
        self.init_engines(databases, **kwargs)
        self.configure_app(app)

    def configure_app(self, app):
        """
        Configure a :class:`fresco.core.FrescoApp` by applying middleware.
        """
        app.add_middleware(SQLAlchemyMiddleware, self)
        return app

    def getsession(self, name='default'):
        """
        Return any named SQLAlchemy session
        """
        return self.sessionmakers[name]()

    @classmethod
    def of(cls, app):
        return cls.registry[app]


class RequestSessions(object):
    """
    An object made available through the WSGI environ and the request context
    that allows access to SQLAlchemy sessions.
    """

    def __init__(self, sqlalchemy):
        self.sqlalchemy = sqlalchemy
        self.open_sessions = {}

    def __getitem__(self, name):
        if name in self.open_sessions:
            return self.open_sessions[name]
        r = self.open_sessions[name] = self.sqlalchemy.getsession(name)
        return r

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def close(self):
        for item in self.open_sessions:
            self.open_sessions[item].close()


class SQLAlchemyMiddleware(object):

    def __init__(self, app, sqlalchemy):
        self.app = app
        self.sqlalchemy = sqlalchemy

    def __call__(self, environ, start_response):
        sessions = RequestSessions(self.sqlalchemy)
        environ[self.sqlalchemy.environ_key] = sessions
        setattr(context, self.sqlalchemy.context_key, sessions)
        try:
            iterator = self.app(environ, start_response)
        except Exception:
            sessions.close()
            raise
        return ClosingIterator(iterator, sessions.close)


def autocommit(session_name='default', retry=True, retry_on=None,
               always_commit=False, backoff=0.1, max_attempts=5,
               sqlalchemy=None):
    """
    Call session.commit() after a successful call to ``func``, or rollback
    in case of error.

    If an error is raised due to a concurrent update, this decorator will
    re-run the request.

    :param session_name: which session to use.
    :param retry: If ``True`` conflicting changes will be retried
                    automatically
    :param retry_on: List of exceptions to retry the request on
    :param always_commit: If true, commit the store unless an exception is
                        raised. The default is to rollback if an HTTP error
                        response is returned.
    :param backoff: How long (in seconds) to wait before retrying the
                        function in the event of an error. The retry time
                        will be doubled at each unsuccessful attempt. The
                        actual time used is randomized to help avoid
                        conflicts.
    :param max_attempts: How many attempts to make in total before rolling
                        back and re-raising the last error received

    :param sqlalchemy: The SQLAlchemy instance to use
    """
    if sqlalchemy is None:
        getsession = lambda name: context.sqlalchemy[name]
    else:
        getsession = lambda name: sqlalchemy[name]
    if retry:
        retry_on = retry_on or retryable_errors

    init_backoff = backoff

    def decorator(func):

        @wraps(func)
        def decorated(*args, **kwargs):
            session = getsession(session_name)

            attempts = max_attempts
            backoff = init_backoff
            while True:
                try:
                    result = func(*args, **kwargs)
                    break
                except retry_on as e:
                    session.rollback()
                    logger.warn('autoretry %r; backoff=%g', e, backoff)
                    sleep(random() * backoff * 2)
                    backoff *= 2
                    attempts -= 1
                    if attempts == 0:
                        raise

                except DBAPIError as e:
                    raise

                except Exception:
                    session.rollback()
                    raise

            if always_commit or not isinstance(result, Response) \
                    or 200 <= result.status_code < 400:
                session.commit()
            else:
                session.rollback()
            return result

        return decorated
    return decorator
