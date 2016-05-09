import os

# Python 2 (with `future`) and Python 3 compatibility.
from configparser import ConfigParser as Parser, NoOptionError


class Settings(object):
    """
    An object for parsing configuration files for mezzanine-client.
    """

    # Parsers
    # User settings (`~/.mezzanine.cfg`) take precedence over the defaults provided in this class.
    parsers_available = ['user', 'defaults']

    def __init__(self):
        """
        Create the settings object.
        """

        # Initialize cache.
        self._cache = {}

        # Initialize default settings.
        defaults = {
            'api_url': 'http://127.0.0.1:8000/api',
            'client_id': '',
            'client_secret': '',
            'refresh_token': '',
            'verbose': 'false',
        }
        self._defaults = Parser(defaults=defaults)
        self._defaults.add_section('general')

        # Initialize a parser for the user settings file.
        self._user = Parser()
        self._user.add_section('general')

        # If the user settings file exists, read it into the parser object.
        user_filename = os.path.expanduser('~/.mezzanine.cfg')
        self._user.read(user_filename)

    def __getattr__(self, key):
        """
        Get the value of a setting.
        """

        # If value is already cached, return the cached value.
        if key in self._cache:
            return self._cache[key]

        # Run through each of the parsers in order of precedence and return the value when found.
        for parser in self.get_parsers:
            # Try to get the value from this parser if it exists.
            try:
                value = parser.get('general', key)
            except NoOptionError:
                # The key is not present in this parser, so check for it in the next parser.
                continue

            # Try to automatically determine the correct type of value. Defaults to string.
            type_methods = ('getint', 'getfloat', 'getboolean')
            for type_method in type_methods:
                try:
                    value = getattr(parser, type_method)('general', key)
                    break
                except ValueError:
                    pass

            # Cache the value for subsequent requests.
            self._cache[key] = value

            return self._cache[key]

        # Raise an exception when the attribute was not found and also there is no default.
        raise AttributeError('The setting `{}` does not exist!'.format(key.lower()))

    @property
    def get_parsers(self):
        """
        Return a tuple of all parsers in order of precedence.
        """
        return tuple([getattr(self, '_{}'.format(i)) for i in self.parsers_available])


# Construct the `settings` object.
settings = Settings()
