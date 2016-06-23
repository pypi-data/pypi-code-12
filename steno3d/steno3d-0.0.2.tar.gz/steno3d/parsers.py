"""parsers.py creates the groundwork for parsers to be plugged in to
steno3d. When a parser is imported, it gets added to the steno3d.parsers
namespace.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import with_metaclass as _with_metaclass
from properties import PropertyClass as _PropertyClass
from six import string_types as _string_types


class _ParserMetaClass(type):
    """Metaclass to ensure Parser classes fit the requried format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != '_BaseParser':
            assert 'extensions' in attrs, \
                "You must say the extensions that are in the {name} parser. " \
                "e.g. ('obj',)".format(name=name)
            assert isinstance(attrs['extensions'], tuple), \
                'The `extensions` in the {name} parser must be a tuple of ' \
                'known extensions.'.format(name=name)
            for ext in attrs['extensions']:
                assert isinstance(ext, _string_types), \
                    'Extensions in the {name} parser must be ' \
                    'strings'.format(name=name)
        new_class = super(_ParserMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class _BaseParserMetaClass(_ParserMetaClass,
                           _PropertyClass.__class__):
    """Augmented metaclass for parsers, inherits from properties
    metaclass
    """


class _BaseParser(_with_metaclass(_BaseParserMetaClass,
                                  _PropertyClass)):
    """Base class for Steno3D parser objects"""


class _DirectorMetaClass(type):
    """Metaclass to ensure Director classes fit the requried format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != 'AllParsers':
            assert name.startswith('AllParsers_'), \
                "Parser classes that inherit 'AllParsers' such as {name} " \
                "must have names that start with " \
                "'AllParsers_'".format(name=name)
            assert 'extensions' in attrs, \
                "{name} must contain a dictionary of extensions and " \
                "parsers".format(name=name)
            assert isinstance(attrs['extensions'], dict), \
                "{name} extensions must be a dictionary of extensions and " \
                "supporting parser".format(name=name)
            for ext in attrs['extensions']:
                assert isinstance(ext, _string_types), \
                    'Extensions in {name} must be strings'.format(name=name)
                assert issubclass(type(attrs['extensions'][ext]),
                                  _BaseParserMetaClass), \
                    'Extensions in {name} must direct to a ' \
                    'Parser class'.format(name=name)
        new_class = super(_DirectorMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class _BaseDirectorMetaClass(_DirectorMetaClass,
                             _PropertyClass.__class__):
    """Augmented metaclass for parser Directors, inherits from
    properties metaclass
    """


class AllParsers(_with_metaclass(_BaseDirectorMetaClass,
                                 _PropertyClass)):
    """Base class for Steno3D parser objects that parse all
    available file types
    """

    def __new__(cls, filename, **kwargs):
        if getattr(cls, 'extensions', None) is None:
            cls.extensions = dict()
            parser_keys = [
                k for k in globals()
                if (
                    k != '_BaseParser' and
                    issubclass(type(globals()[k]), _BaseParserMetaClass)
                )
            ]
            for k in parser_keys:
                for ext in globals()[k].extensions:
                    if ext not in cls.extensions:
                        cls.extensions[ext] = globals()[k]
                    elif issubclass(type(cls.extensions[ext]),
                                    _BaseParserMetaClass):
                        cls.extensions[ext] = (cls.extensions[ext].__name__ +
                                               ', ' + globals()[k].__name__)
                    else:
                        cls.extensions[ext] = (cls.extensions[ext] +
                                               ', ' + globals()[k].__name__)

        for ext in cls.extensions:
            if filename.split('.')[-1] == ext:
                if not issubclass(type(cls.extensions[ext]),
                                  _BaseParserMetaClass):
                    raise ValueError(
                        '{ext}: file type supported by more than one parser. '
                        'Please specify one of ({parsers})'.format(
                            ext=ext,
                            parsers=cls.extensions[ext]
                        )
                    )
                return cls.extensions[ext](filename, **kwargs)

        raise ValueError(
            '{bad}: unsupported file extensions. Must be in ({ok})'.format(
                bad=filename.split('.')[-1],
                ok=', '.join(list(cls.extensions))
            )
        )

try:
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
