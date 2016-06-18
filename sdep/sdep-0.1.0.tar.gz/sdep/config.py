"""
This file contains the `Configuration` class as well as related classes
necessary for controlling `sdep` configuration.
"""

# pylint: disable=import-error

import os
import simplejson as json

class ConfigFileDoesNotExistError(Exception):
    """
    A specialized error we raise when we cannot find a file to use for
    configuration.
    """
    # pylint: disable=too-few-public-methods
    pass

class ConfigImproperFormatError(Exception):
    """
    A specialized error we raise when the user specifies the configuration in an
    improper format.
    """
    # pylint: disable=too-few-public-methods
    pass

class ConfigParseError(Exception):
    """
    A specialized error we raise when for whatever reason we cannot create the
    configuration object.
    """
    # pylint: disable=too-few-public-methods
    pass

class Config(object):
    """
    A class for controlling the configuration of an `sdep` instance.

    Args:
        config_file(Optional[str]): The path to the configuration file used to
            generate the config. If no configuration file is given, then we look
            in the directory from which we are running `sdep` and then the
            user's home directory.
        test_mode(Optional[bool]): A flag indicating whether we should
            prepopulate this `Config` instance with a working default
            configuration. This field should only be used in testing, when we
            wish to create an instance of `Sdep`, but do not want to create a
            custom config in a file or environment variables.

    Returns:
        config: An instance of the `Config` class, filled in with all values
            from either a configuration file or environment variables.

    Raises:
        ConfigParseException: If either configuration does not exist or is
            improperly specified.
    """
    # pylint: disable=too-few-public-methods

    # Unless otherwise specified, we assume the config file is named `.sdeprc`.
    DEFAULT_CONFIG_FILE_NAME = ".sdeprc"

    # Constant names for fields.
    AWS_ACCESS_KEY_ID_FIELD = "aws_access_key_id"
    AWS_SECRET_ACCESS_KEY_FIELD = "aws_secret_access_key"
    SITE_DIR_FIELD = "site_dir"
    DOMAIN_FIELD = "domain"
    INDEX_SUFFIX_FIELD = "index_suffix"
    ERROR_KEY_FIELD = "error_key"

    def __init__(self, config_file=None, test_mode=False):
        # @TODO I wonder if it would make more sense for the `Config` class to
        # inherit from `Hash`, and then we wouldn't need to define
        # `self._config_hash` or `self.get`. However, I'm a little worried about
        # having to deal with all of the extra methods that come with a `Hash`.
        self._config_hash = {}

        if test_mode:
            self._prepopulate_config()
        else:
            if config_file is None or not os.path.isfile(config_file):
                config_file = self.locate_config_file()
            else:
                config_file = os.path.join(os.getcwd(), config_file)

            try:
                if config_file is None:
                    self._parse_from_env()
                else:
                    self._parse_from_config_file(config_file)

            except (ConfigFileDoesNotExistError, ConfigImproperFormatError):
                raise ConfigParseError

    def get(self, field):
        """
        Get a configuration value for the specified field. This is the ONLY way
        we should be inquiring about configuration values.

        Args:
            field (str): The field for which we want the configuration value.

        Returns:
            str: The value for the specified field or `None` if the value has no
            specified configuration.
        """
        return self._config_hash.get(field)

    def put(self, field, value):
        """
        Insert a `value` for the specified configuration `field`. If the given
        `field` already has a value, we will overwrite it with `value`.

        Args:
            field (str): The configuration field.
            value (object): The value for said field.
        """
        self._config_hash[field] = value

    @classmethod
    def locate_config_file(cls):
        """
        Determine if a configuration file exists either in the current directory
        or the home directory.

        Returns:
            str: The path to the configuration file or `None` if no path is
                specified.
        """
        curr_dir_file = os.path.join(os.getcwd(), cls.DEFAULT_CONFIG_FILE_NAME)
        home_dir_file = os.path.join(os.path.expanduser("~"),
                                     cls.DEFAULT_CONFIG_FILE_NAME)

        for poss_config_file in [curr_dir_file, home_dir_file]:
            if os.path.isfile(poss_config_file):
                return poss_config_file

        return None

    def _parse_from_env(self):
        """
        Fill in the instance of `Config` with the information contained in the
        environment variables.

        Raises:
            ConfigImproperFormatError: If vital configuration data is either in
                the incorrect format or nonexistent.
        """
        self._config_hash = self._parse_from_store(
            self.required_config_fields(env=True),
            self.optional_config_fields(env=True),
            os.environ
        )

    def _parse_from_config_file(self, config_file):
        """
        Fill in the instance of `Config` with the information contained in
        `config_file`. The configuration file MUST be in JSON format.

        Args:
            config_file (str): The path to the configuration file.

        Raises:
            ConfigImproperFormatError: If vital configuration data is either in
                the incorrect format or nonexistent.
        """
        config_data = {}

        try:
            with open(config_file) as json_file:
                config_data = json.loads(json_file.read())
        except (IOError, json.JSONDecodeError):
            raise ConfigImproperFormatError

        self._config_hash = self._parse_from_store(
            self.required_config_fields(env=False),
            self.optional_config_fields(env=False),
            config_data
        )

    @classmethod
    def _parse_from_store(cls, required_fields, optional_fields, data_store):
        """
        Parse the configuration from a data store object (i.e. the json hash or
        `os.environ`). This method is useful because the process for parsing the
        data from either the environment or a configuration file shares many of
        the same components. Abstracting to a single method ensures less
        duplicate code.

        Args:
            required_fields (list): A list of the required fields.
            optional_fields (list): A list of the optional fields.
            data_store (dict): A dictionary containing key/value pairs with the
                fields as a key.

        Returns:
            dict: A configuration dictionary.
        """
        # Start with all of the defaults filled in. We will overwrite with any
        # specified info.
        config_hash = cls._optional_fields_and_defaults()

        fields = [(f, True) for f in required_fields] + [(f, False) for f in optional_fields]

        for field, required in fields:
            value = data_store.get(field)

            if value is None:
                if required:
                    raise ConfigImproperFormatError
            else:
                config_hash[field.lower()] = value

        return config_hash

    @classmethod
    def required_config_fields(cls, env=False):
        """
        Return the required configuration fields either in `snake_case` or in all
        upper-case `snake_case`, depending on whether the `env` flag is set.

        Args:
            env (bool): A boolean flag indicating what capitalization we should
                use when returning the fields.

        Returns:
            [str]: A list of required configuration fields.
        """
        required_fields = [
            cls.AWS_ACCESS_KEY_ID_FIELD,
            cls.AWS_SECRET_ACCESS_KEY_FIELD,
            cls.SITE_DIR_FIELD,
            cls.DOMAIN_FIELD
        ]

        if env:
            return [field.upper() for field in required_fields]
        else:
            return required_fields

    @classmethod
    def optional_config_fields(cls, env=False):
        """
        Return the optinal configuration fields either in `snake_case` or in all
        upper-case `snake_case`, depending on whether the `env` flag is set.

        Args:
            env (bool): A boolean flag indicating what capitalization we should
                use when returning the fields.

        Returns:
            [str]: A list of optional configuration fields.
        """
        optional_fields = list(cls._optional_fields_and_defaults().keys())

        if env:
            return [field.upper() for field in optional_fields]
        else:
            return optional_fields

    @classmethod
    def _optional_fields_and_defaults(cls):
        """
        Return a dictionary of optional fields and their defaults.

        Returns:
            dict: Optional fields and their defaults.
        """
        return {
            cls.INDEX_SUFFIX_FIELD: "index.html",
            cls.ERROR_KEY_FIELD: "404.html"
        }

    def _prepopulate_config(self):
        """
        Prepopulate this instance of `Config` with sensible default values which
        we can use when testing.
        """
        populate_hash = {
            self.AWS_ACCESS_KEY_ID_FIELD: "MY_ACCESS_KEY",
            self.AWS_SECRET_ACCESS_KEY_FIELD: "MY_SECRET_KEY",
            self.SITE_DIR_FIELD: "./static",
            self.DOMAIN_FIELD: "sdep-test.com"
        }

        self._config_hash = self._parse_from_store(
            self.required_config_fields(env=False),
            self.optional_config_fields(env=False),
            populate_hash
        )
