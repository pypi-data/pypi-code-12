
class RakamError(Exception):
    """
        Generic rakam error.
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
