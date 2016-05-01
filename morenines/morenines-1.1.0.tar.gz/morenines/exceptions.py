class MoreninesError(Exception):
    """The base class for unrecoverable errors during morenines execution."""

class PathError(MoreninesError):
    """Errors involving user-supplied path arguments."""

    def __init__(self, message, path, *args):
        self.path = path

        super(PathError, self).__init__(message, *args)


class RepositoryError(MoreninesError):
    """Errors in reading from or writing to a repository."""


class MoreninesWarning(Exception):
    """The base class for unexpected but recoverable situations during morenines execution."""

class NoEffectWarning(MoreninesWarning):
    """Situations where specific user input has yielded no change in repository state."""
