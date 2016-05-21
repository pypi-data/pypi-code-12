class AWSError(Exception):
    pass

class AWSCredentialsMissing(AWSError):
    pass

class InvalidSchemeException(ValueError):
    pass

class S3Exception(AWSError):
    pass

class KeyNotFound(S3Exception):
    pass

class KeyExists(S3Exception):
    pass

class _TransientError(RuntimeError):
    pass

def get_transient_error_class():
    try:
        from guts.service.exceptions import TransientError  # That, precisely, is the point. pylint: disable=no-name-in-module
        return TransientError
    except ImportError:
        return _TransientError

class S3Warning(RuntimeWarning):
    pass

class EventualConsistencyWarning(S3Warning):
    pass
