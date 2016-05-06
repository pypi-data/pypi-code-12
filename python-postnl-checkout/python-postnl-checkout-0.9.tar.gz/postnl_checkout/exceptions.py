class PostNLException(Exception):
    """ Exception class for use with PostNLCheckout. """
    pass


class PostNLRequestException(PostNLException):
    """
    Exceptions raised due to request values.

    Essentially a wrapper around CIFException, providing worthwhile feedback.
    """
    pass


class PostNLResponseException(PostNLException):
    """ Exceptions due to values in the response. """
    pass
