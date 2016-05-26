'''
Woodstove exceptions
'''


class BaseWoodstoveException(Exception):
    ''' Base of all woodstove exceptions '''
    trace = False


class NotFoundException(BaseWoodstoveException):
    ''' Exception for not found situations '''


class RequestException(BaseWoodstoveException):
    ''' Problem in the request '''


class LoginException(BaseWoodstoveException):
    ''' Login failure '''


class JobException(BaseWoodstoveException):
    ''' Job Exception '''


class TimeoutException(BaseWoodstoveException):
    ''' Raised when an ssh command times out '''


class ArgumentException(BaseWoodstoveException):
    ''' Argument Exception Exception '''


class AuthException(BaseWoodstoveException):
    ''' Auth Exception Exception '''


class InternalException(BaseWoodstoveException):
    ''' Internal error '''
    trace = True


class HookStopException(BaseWoodstoveException):
    ''' A hook is requesting the stop of further processing '''
