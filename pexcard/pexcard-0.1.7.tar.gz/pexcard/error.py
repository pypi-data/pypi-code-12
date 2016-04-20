class PexError(Exception):
    def __init__(self, message, request_url, request_params,
                 status_code, response):
        super(PexError, self).__init__(message)

        self._message = message
        self.request_url = request_url
        self.request_params = request_params
        self.response = response
        self.status_code = status_code


class RateLimitError(PexError):
    pass


class InvalidPexResponseError(PexError):
    pass


class AuthenticationError(PexError):
    pass


class InvalidRequestError(PexError):
    pass


class APIError(PexError):
    pass


class RequesterForbiddenError(PexError):
    pass


class PexServerSideError(PexError):
    pass


class InvalidPexServerResponseError(PexServerSideError):
    pass
