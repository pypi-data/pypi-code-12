#   Copyright 2015-2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import cherrypy

import psycopg2.pool

COMMITABLE_HANDLER_EXCEPTIONS = (
    cherrypy.HTTPRedirect, cherrypy.InternalRedirect, cherrypy.NotFound)
DSN_PREFIX = "fallback_application_name='cherrypy_psycopg2'"


class Psycopg2Tool(cherrypy.Tool):
    def __init__(self, point='before_handler', name=None, priority=50):
        self._point = point
        self._name = name
        self._priority = priority

        self._pools = {}

    def callable(self, minconn, maxconn, dsn, cursor_factory=None):
        dsn = DSN_PREFIX + ' ' + dsn

        pool = self._pools.get(dsn, None)

        if not pool:
            pool = psycopg2.pool.ThreadedConnectionPool(
                minconn, maxconn, dsn=dsn, cursor_factory=cursor_factory)
            self._pools[dsn] = pool

        innerfunc = cherrypy.serving.request.handler

        def wrap(*args, **kwargs):
            connection = None
            connection_attempt = 0

            while not connection:
                connection_attempt += 1
                connection = pool.getconn()

                try:
                    connection.reset()
                except:
                    pool.putconn(connection, close=True)

                    connection = None

                    # Up to maxconn connections may fail (server restart)
                    if connection_attempt > maxconn:
                        msg = "No working database connections\n"
                        cherrypy.log.error(msg=msg, traceback=True)
                        raise cherrypy.HTTPError(
                            message="psycopg2 connection failure")

                    msg = "Database connection failed (attempt {} of {})\n"
                    msg = msg.format(connection_attempt, maxconn)
                    cherrypy.log.error(msg=msg, traceback=True)

            cherrypy.request.psycopg2_connection = connection
            cherrypy.request.psycopg2_cursor = connection.cursor()

            try:
                response = innerfunc(*args, **kwargs)
            except COMMITABLE_HANDLER_EXCEPTIONS:
                connection.commit()
                raise
            except:
                connection.rollback()
                raise
            else:
                connection.commit()
            finally:
                pool.putconn(connection)

            return response

        cherrypy.serving.request.handler = wrap


def install_tool():
    cherrypy.tools.psycopg2 = Psycopg2Tool()
