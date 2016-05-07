class BaseException(Exception):
    pass


class ImportModuleErrorException(BaseException):
    pass


class CommandNotRegisteredException(BaseException):
    pass


class CommandAlreadyRegisteredException(BaseException):
    pass
