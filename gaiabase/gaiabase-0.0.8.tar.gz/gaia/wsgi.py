# -*- coding: utf-8 -*-

import json
import flask

from functools import wraps
from io import BytesIO
from flask import send_file


def api(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
        except BaseException as e:
            value = {
                "status": "failed",
                "error": "Unkonwn error!"
            }
            flask.current_app.logger.error("Unkonwn error: %s" % str(e))
            flask.current_app.logger.exception(e)

        status = 200
        mimetype = 'application/json'
        content = json.dumps(value)
        callback = flask.request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + content + ')'
            mimetype = 'application/javascript'

        return flask.current_app.response_class(content, status=status, mimetype=mimetype)
    return decorated_function


def wrap_img(func, imgtype):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            mimetype = 'image/%s' % imgtype
            fake_file = BytesIO()
            im = func(*args, **kwargs)
            im.save(fake_file, imgtype)
            fake_file.seek(0)
            return send_file(fake_file, mimetype=mimetype)
        except BaseException as e:
            flask.current_app.logger.error("Unkonwn error: %s" % str(e))
            flask.current_app.logger.exception(e)
            return flask.current_app.make_response(('', 502, []))

    return decorated_function


def img(imgtype='png'):
    def wrapper(func):
        return wrap_img(func, imgtype)
    return wrapper


def png(func):
    return wrap_img(func, 'png')


def jpeg(func):
    return wrap_img(func, 'jpeg')

