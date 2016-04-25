

class CommandError(Exception):
    def __init__(self, *args, **kwargs):
        self.err_code = kwargs.pop('err_code', None)
        super(CommandError, self).__init__(*args, **kwargs)


class ConfigError(CommandError):
    def __init__(self, *args, **kwargs):
        kwargs['err_code'] = 1
        super(ConfigError, self).__init__(*args, **kwargs)
