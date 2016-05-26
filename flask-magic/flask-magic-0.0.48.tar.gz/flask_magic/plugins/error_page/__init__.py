"""
Error Page

This plugin to display customize error page

Can be called as standalone
"""
from __future__ import division
import logging
from flask_magic import (Magic, set_meta, register_package, abort)
from flask_magic import exceptions
from sqlalchemy.exc import SQLAlchemyError

register_package(__package__)

# A callback function to use as renderer instead of the built in one
# A use case can be
renderer = None

"""
Example:

@render_as_json
def my_error(e):
    return {
        "error": True,
        "code": e.code,
        "message": e.description
    }, e.code
renderer = my_error
"""




class SQLAlchemyHTTPException(exceptions.HTTPException):

    code = 500
    description = "SQLAlchemy Error"

    def __init__(self, error):
        """Takes an optional list of valid http methods
        starting with werkzeug 0.3 the list will be mandatory."""
        exceptions.HTTPException.__init__(self, self.description)
        #self.valid_methods = valid_methods
        # statement, params, orig, message


    @classmethod
    def wrap(cls, exception, name=None):
        """This method returns a new subclass of the exception provided that
        also is a subclass of `BadRequest`.
        """
        ("SQLAlchemy Error")
        httpexc.code = 500
        return httpexc


def view(template_dir=None):

    if not template_dir:
        template_dir = "Magic/Plugin/ErrorPage"
    template_page = "%s/index.html" % template_dir

    class ErrorPage(Magic):

        @classmethod
        def register(cls, app, **kwargs):
            super(cls, cls).register(app, **kwargs)

            @app.errorhandler(400)
            @app.errorhandler(401)
            @app.errorhandler(403)
            @app.errorhandler(404)
            @app.errorhandler(405)
            @app.errorhandler(406)
            @app.errorhandler(408)
            @app.errorhandler(409)
            @app.errorhandler(410)
            @app.errorhandler(413)
            @app.errorhandler(414)
            @app.errorhandler(429)
            @app.errorhandler(500)
            @app.errorhandler(501)
            @app.errorhandler(502)
            @app.errorhandler(503)
            @app.errorhandler(504)
            @app.errorhandler(505)
            @app.errorhandler(SQLAlchemyError)
            def register_error(error):

                if isinstance(error, SQLAlchemyError):
                    error = SQLAlchemyHTTPException(error)

                # we'll log non 4** errors
                if int(error.code // 100) != 4:
                    _error = str(error)
                    _error += " - HTTException Code: %s" % error.code
                    _error += " - HTTException Description: %s" % error.description
                    logging.error(_error)

                if renderer:
                    return renderer(error)
                else:
                    set_meta(title="Error %s" % error.code)
                    return cls.render_(error=error, template_=template_page), error.code

    return ErrorPage

error_page = view()