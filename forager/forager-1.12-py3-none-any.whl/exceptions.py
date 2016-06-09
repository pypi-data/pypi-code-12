class ForagerException(Exception):
    pass


class HttpException(ForagerException):
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HttpException, self).__init__(*args, **kwargs)


class Unauthorized(HttpException):
    pass


class Forbidden(HttpException):
    pass
