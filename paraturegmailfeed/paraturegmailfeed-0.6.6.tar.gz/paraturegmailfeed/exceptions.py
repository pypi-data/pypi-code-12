# exceptions.py
"""Module contains custom exceptions.
"""


class Error(Exception):
    """Base-class for all exceptions raised by this package."""


class MatchNotFound(Error):
    """Regex search did not return any matches."""


class MongoDbConnectionError(Error):
    """Pymongo could not connect to mongod."""
