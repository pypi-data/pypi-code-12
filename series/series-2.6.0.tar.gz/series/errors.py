from tek.errors import TException


class MissingMetadata(TException):
    pass


class SeriesException(TException):
    pass


class InvalidDBError(SeriesException):
    def __init__(self, specifics):
        text = 'Invalid database: {}'
        super().__init__(text.format(specifics))


class SeriesDException(SeriesException):
    pass
