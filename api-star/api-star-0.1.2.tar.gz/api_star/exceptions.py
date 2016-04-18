class APIException(Exception):
    code = 500
    description = 'An error occurred.'

    def __init__(self, description=None, code=None):
        if description is not None:
            self.description = description
        if code is not None:
            self.code = code

    def __str__(self):
        return '%s' % self.description


class BadRequest(APIException):
    code = 400
    description = 'Malformed request.'


class ValidationError(APIException):
    code = 400
    description = 'Invalid data in request.'


class Unauthorized(APIException):
    code = 401
    description = 'Incorrect authentication credentials.'


class Forbidden(APIException):
    code = 403
    description = 'You do not have permission to perform this action.'


class NotFound(APIException):
    code = 404
    description = 'No resource could be found at this URL.'


class NotAcceptable(APIException):
    code = 406
    description = 'The request `Accept` header could not be satisfied.'


class UnsupportedMediaType(APIException):
    code = 415
    description = 'Unsupported media type in the request `Content-Type` header.'
