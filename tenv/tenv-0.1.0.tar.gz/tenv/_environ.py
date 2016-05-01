from typing import Dict, List


class ImproperlyConfiguredError(Exception):
    pass


# Cannot rely on None since it may be desired as a return value.
NOTSET = type(str('NoValue'), (object,), {})
# Boolean true strings
TRUE_VALUES = ('true', 'on', 'ok', 'y', 'yes', '1')

class _Environment(object):
    def __init__(self, env_dict: Dict[str, str] = None):
        self.variables = env_dict

    def __contains__(self, item: str) -> bool:
        return item in self.variables

    def get(self, var: str, default=NOTSET) -> str:
        value = self.variables.get(var)
        if value is None:
            if default is NOTSET:
                error_msg = "Environment variable '{}' not set.".format(var)
                raise ImproperlyConfiguredError(error_msg)
            else:
                value = default

        # no casts in plain get()
        return value

    ## specific get()'s
    def getbool(self, var: str, default=NOTSET) -> bool:
        value = self.get(var, default=default)
        if value == default:
            return value

        return value.lower() in TRUE_VALUES

    def getint(self, var: str, default=NOTSET) -> int:
        value = self.get(var, default=default)
        if value == default:
            return value

        return int(value)

    def getfloat(self, var: str, default=NOTSET) -> float:
        value = self.get(var, default=default)
        if value == default:
            return value

        return float(value)

    def getlist(self, var: str, default=NOTSET) -> List[str]:
        value = self.get(var, default=default)
        if value == default:
            return value

        return list(value.split(','))