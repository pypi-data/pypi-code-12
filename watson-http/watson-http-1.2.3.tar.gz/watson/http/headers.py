# -*- coding: utf-8 -*-
from watson.common.datastructures import MultiDict
from watson.common.imports import get_qualified_name

MISSED_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH', 'HTTPS')


class ServerCollection(object):
    """Retrieves server related variables from an environ.

    Example:

    .. code-block:: python

        server = ServerCollection(environ)
        print(server['SCRIPT_NAME'])
    """
    __slots__ = ('environ')

    def __init__(self, environ=None):
        self.environ = environ or {}

    @classmethod
    def from_environ(cls, environ):
        server = cls(environ)
        return server

    def items(self):
        """Returns tuple pairs of environ vars and their values.
        """
        for field, value in self.environ.items():
            if not field.startswith('HTTP_'):
                yield (field, value)

    def __getitem__(self, key, default=None):
        key = key.replace('HTTP_', '')
        return self.environ.get(key, None)

    def __iter__(self):
        for server in self.items():
            yield server

    def __len__(self):
        return len([server for server in self])


class HeaderCollection(object):
    """Retrieves header related variables from an environ.

    Allows the use of non-capitalized names.

    Example:

    .. code-block:: python

        headers = HeaderCollection.from_environ(environ)
        print(headers.get('Content-Type'))
    """
    __slots__ = ('environ', 'mutable')

    def __init__(self, environ=None):
        self.mutable = True
        self.environ = environ or MultiDict()

    @classmethod
    def from_environ(cls, environ):
        """Instantiate the collection from an existing environ.
        """
        fix_http_headers(environ)
        headers = cls(environ)
        headers.mutable = False
        return headers

    def get(self, field, option=None, default=None):
        """Retrieve an individual header or it's option.

        Example:

        .. code-block:: python

            # Content-Type: text/html; charset=utf-8
            headers = HeaderCollection()
            headers.add('Content-Type', 'text/html', charset='utf-8')
            option = headers.get('Content-Type', 'charset') # utf-8


        Args:
            field: the header field
            option: the option to retrieve from the field
            default: the default value if the option does not exist

        Returns:
            The default value or the value from the option
        """
        if option:
            value = self.__getitem__(field, default)
            if not value:
                return default
            options = value.split('; ')
            found = [opt.split('=')[1]
                     for opt in options if opt.split('=')[0] == option]
            return found[0] if found else default
        return self.__getitem__(field, default)

    # Deprecated in favor of .get()
    get_option = get

    def __getitem__(self, field, default=None):
        field = convert_to_http_field(field)
        return self.environ.get(field, default)

    def set(self, field, value, **options):
        """Add a header to the collection.

        Any existing headers with the same name will be removed.

        Args:
            field (string): The field name
            value (mixed): The value of the field
            options (kwargs): Any additional options for the header

        Example:

        .. code-block:: python

            headers = ...
            headers.add('Content-Type', 'text/html', charset='utf-8')
        """
        self.__setitem__(field, value, replace=True, **options)

    def add(self, field, value, replace=False, **options):
        """Add a header to the collection.

        Args:
            field (string): The field name
            value (mixed): The value of the field
            replace (boolean): Whether or not to replace an existing field
            options (kwargs): Any additional options for the header

        Example:

        .. code-block:: python

            headers = ...
            headers.add('Content-Type', 'text/html', charset='utf-8')
        """
        self.__setitem__(field, value, replace, **options)

    def items(self):
        """Returns tuple pairs of environ vars and their values.
        """
        for field, value in self.environ.items():
            if field.startswith('HTTP_'):
                field = convert_to_wsgi(field[5:])
                yield (field, value)

    # Internals

    def __setitem__(self, field, value, replace=False, **options):
        if self.mutable:
            field = convert_to_http_field(field)
            value = [str(value)]
            if options:
                value.extend(['{0}={1}'.format(key, val) for
                              key, val in options.items()])
            value = '; '.join(value)
            if isinstance(self.environ, MultiDict):
                self.environ.set(field, value, replace)
            else:
                self.environ[field] = value
        else:
            raise TypeError('{0} is not mutable.'.format(get_qualified_name(self)))

    def __delitem__(self, field):
        if self.mutable:
            field = convert_to_http_field(field)
            del self.environ[field]
        else:
            raise TypeError('{0} is not mutable.'.format(get_qualified_name(self)))

    def __contains__(self, field):
        field = convert_to_http_field(field)
        return field in self.environ

    def __iter__(self):
        for header in self.items():
            yield header

    def __len__(self):
        return len([header for header in self])

    def __call__(self):
        """Output in a format suitable for a wsgi callable.

        Outputs the header collection as a list of tuple pairs for use in a
        wsgi application.

        Returns:
            A list of tuple pairs
        """
        tuple_pairs = []
        for field, value in self:
            if (isinstance(value, list)):
                for multi_val in value:
                    tuple_pairs.append((field, multi_val))
            else:
                tuple_pairs.append((field, value))
        return tuple_pairs

    def __str__(self):
        return (
            '\r\n'.join(['{0}: {1}'.format(field, value)
                        for field, value in self()])
        )


def convert_to_wsgi(field):
    """Convert a field name from UPPER_CASE to Title-Case.
    """
    return field.lower().replace('_', ' ').title().replace(' ', '-')


def convert_to_http_field(field):
    """Convert a field from Title-Case to HTTP_UPPER_CASE.
    """
    field = field.upper().replace('-', '_')
    if not field.startswith('HTTP_'):
        field = 'HTTP_' + field
    return field


def fix_http_headers(environ, remove=False):
    """Add HTTP_ to the relevant headers that its not included with.
    """
    for header in MISSED_HEADERS:
        if header in environ:
            environ['HTTP_'+header] = environ[header]
            if remove:
                del environ[header]
