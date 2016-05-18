import base64
import logging
from functools import wraps
from flask import g, request, redirect, url_for, abort
from .models import User


def has_valid_token(request):
    try:
        auth_type, encoded_token = request.headers['Authorization'].split(
            None, 1)
        if auth_type != 'Bearer':
            raise IndexError
        decoded_token = base64.b64decode(encoded_token)
    except ValueError:
        logging.error('The Authorization header is either empty or has no token')
        return False
    except IndexError:
        logging.error('Authorization header not set to Bearer')
        return False
    return User.verify_auth_token(decoded_token)


def id_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if has_valid_token(request):
            return f(*args, **kwargs)
        abort(401)
    return decorated_function
