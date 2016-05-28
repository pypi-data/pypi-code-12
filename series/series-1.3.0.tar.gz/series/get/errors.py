from tek.errors import TException


class SeriesDException(TException):
    pass


class ArchiverError(SeriesDException):
    pass


class InvalidDBError(SeriesDException):
    def __init__(self, specifics):
        text = 'Invalid database: {}'
        super(InvalidDBError, self).__init__(text.format(specifics))
