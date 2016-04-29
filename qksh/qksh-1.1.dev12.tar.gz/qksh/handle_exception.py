# exception class goes here.
import traceback


class QkshError(Exception):
    """
    Base class for exceptions
    """
    message = 'An unexpected error occurred.'

    def __init__(self, error='', remove_stack_frame=-1):
        self.error = error
        super(QkshError, self).__init__(error)

        # stripping off local stack frame
        self.stack = traceback.format_stack()[:remove_stack_frame]

    def __str__(self):
        return self.message

    def dump_error(self):
        stack = "".join(self.stack)
        return 'Stacktrace:\n {0}'.format(stack)


class AuthenticateError(QkshError):
    message = 'Authenticate with F5 website failed.'


class ArgumentError(QkshError):
    message = 'Invalid Argument list.'
