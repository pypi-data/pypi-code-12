"""Module contains Status class. The Status class contains descriptive
class variables representing HTTP status codes.
"""


class Status(object):
    """Name mappings for HTTP status codes"""

    # 200 level
    OK = 200
    CREATED = 201
    NO_CONTENT = 204

    # 300 level
    PERMANENT_REDIRECT = 301
    TEMPORARY_REDIRECT = 302

    # 400 level
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    REQUEST_TIMEOUT = 408
    CONFLICT = 409

    # 500 level
    SERVER_ERROR = 500
