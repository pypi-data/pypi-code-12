"""
Module defining a specific exception for the errors occuring while analyzing
a DTD.

.. autoclass:: DtdError
   :show-inheritance:
"""

class DtdError(Exception):
    """
    Exception raised when finding an error while analyzing a DTD.
    """
    pass

