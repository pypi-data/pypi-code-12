
class RakamError(Exception):
    """
        Generic rakam error.
    """
    pass


class MissingKey(Exception):
    """
        Required key for the action is not provided.
    """
    pass


class InvalidKeyError(RakamError):
    """
        Key is used for other type of requests.
    """
    pass


class BadKeyError(RakamError):
    """
        Key doesn't belong to your project.
    """
    pass


class ConflictError(RakamError):
    """
        Raised when same action is already being processed
    """
    pass


class RakamSqlError(RakamError):
    pass


class BadSqlResponse(RakamSqlError):
    """
        Sql result body is invalid.
    """
    pass


class SqlRequestFailed(RakamSqlError):
    """
        If sql query fails.
    """
    pass


class BadSqlMetadata(RakamSqlError):
    """
        Invalid metadata.
    """
    pass


class BadSqlResult(RakamSqlError):
    """
        Invalid result.
    """
    pass
