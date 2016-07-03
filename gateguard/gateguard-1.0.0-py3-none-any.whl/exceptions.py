# coding=utf-8


class GateguardError(Exception):

    pass


class ValidationError(GateguardError):

    def __init__(self, error=None):
        self.error = error

        super().__init__(self.error)
