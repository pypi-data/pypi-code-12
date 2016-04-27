""" This module provides the exceptions."""

class DOIError(Exception):
    """
    Base class for exceptions in this module.

    """
    pass

class ExternalError(DOIError):
    """
    Exceptions resulting from communication with external services.

    """
    pass
