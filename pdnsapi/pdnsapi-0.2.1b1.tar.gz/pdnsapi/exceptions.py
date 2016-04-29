class PDNSException(BaseException):
    pass


class PDNSNotFoundException(PDNSException):
    pass


class PDNSAccessDeniedException(PDNSException):
    pass


class PDNSProtocolViolationException(PDNSException):
    pass


class PDNSServerErrorException(PDNSException):
    pass
