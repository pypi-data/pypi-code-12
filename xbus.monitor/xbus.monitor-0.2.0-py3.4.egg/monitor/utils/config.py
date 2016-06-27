"""Utilities for the configuration file.
"""


def tobool(value):
    """helper to evaluate a string into a boolean
    WARNING: at the moment value is True by default unless it can
    be evaluated to False matching one of (case insensitive):
        ('false', 'no', 'n', '0')

    :param value: the string to evaluate
    :type value: string

    :returns: True or False depending on the given value
    """
    if value.lower() in ('false', 'no', 'n', '0'):
        value = False

    else:
        value = True

    return value


def bool_setting(config, setting):
    """Read a boolean setting from the configuration file; that setting may be
    expressed as a string.
    """

    value = config.get(setting, True)

    if isinstance(value, str):
        value = tobool(value)

    return value
