from functools import wraps
from flask import request, current_app


def jsonp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(f(*args, **kwargs))
            content = str(callback) + '(' + data + ')'
            mime_type = 'application/javascript'
            return current_app.response_class(content, mimetype=mime_type)
        else:
            return f(*args, **kwargs)
    return decorated_function
