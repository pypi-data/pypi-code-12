import re
import sys
from collections import defaultdict
from six.moves.configparser import RawConfigParser


class RawCaseSensitiveConfigParser(RawConfigParser):
    optionxform = str


def get_interpretation_by_name(settings, prefix, interpret_setting):
    interpretation_by_name = defaultdict(dict)
    pattern_key = re.compile(prefix.replace('.', r'\.') + r'(.*)\.(.*)')
    for key, value in settings.items():
        try:
            name, attribute = pattern_key.match(key).groups()
        except AttributeError:
            continue
        interpretation = interpretation_by_name[name]
        interpretation.update(interpret_setting(attribute, value))
    return interpretation_by_name


def unicode_(x):
    # http://stackoverflow.com/a/23085282/192092
    if not hasattr(x, 'decode'):
        return x
    return x.decode(sys.getfilesystemencoding())
