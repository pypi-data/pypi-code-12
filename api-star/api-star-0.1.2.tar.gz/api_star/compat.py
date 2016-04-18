import binascii
import inspect
import sys


PY3 = sys.version_info[0] == 3


if PY3:
    string_types = (str,)
    text_type = str
    COMPACT_SEPARATORS = (',', ':')   # Compact JSON
    VERBOSE_SEPARATORS = (',', ': ')  # Indented JSON

    from urllib.parse import urlparse  # noqa

    def copy_signature(copy_from, copy_to):
        copy_to.__signature__ = inspect.signature(copy_from)

    def getargspec(func):
        return inspect.getargspec(func)

    Base64DecodeError = binascii.Error

else:
    string_types = (type(b''), type(u''))
    text_type = unicode
    COMPACT_SEPARATORS = (b',', b':')   # Compact JSON
    VERBOSE_SEPARATORS = (b',', b': ')  # Indented JSON

    from urlparse import urlparse  # noqa

    def copy_signature(copy_from, copy_to):
        # inspect.signature does not exists.
        # Save the argspec information on a private attribute,
        # so that `getargspec()` can retrieve it.
        copy_to._argspec = getargspec(copy_from)

    def getargspec(func):
        return getattr(func, '_argspec', inspect.getargspec(func))

    Base64DecodeError = TypeError
