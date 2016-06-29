class HatcherException(Exception):
    pass


class MissingFilenameError(HatcherException):
    pass


class MissingPlatformError(HatcherException):
    pass


class ChecksumMismatchError(HatcherException):
    pass


class InvalidRuntime(HatcherException):
    pass


class InvalidEgg(HatcherException):
    pass
