class AmbisafeError(Exception):
    def __init__(self, message, error):
        self.message = message
        self.error = error

    def __str__(self):
        return self.message


class ClientError(AmbisafeError):
    def __repr__(self):
        return '<AmbisafeClientError error="{}" message="{}">'.format(self.error, self.message)


class ServerError(AmbisafeError):
    def __repr__(self):
        return '<AmbisafeClientError error="{}" message="{}">'.format(self.error, self.message)
