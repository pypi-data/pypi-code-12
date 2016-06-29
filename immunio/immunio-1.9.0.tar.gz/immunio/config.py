from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ConfigParser import SafeConfigParser
import errno
import io
import json
import os

from immunio.exceptions import ConfigError
from immunio.logger import log


CONFIG_FILENAME = "immunio.ini"
# Remove the legacy filename once existing customers have migrated.
CONFIG_LEGACY_FILENAME = "immunio.json"

IMMUNIO_SECTION_NAME = "immunio"


class Config(object):
    def __init__(self, defaults=None, autoload=True):
        # Initialize to default configuration (if specified)
        self._config = defaults or {}
        log.debug("Default configuration: %(config)s", {
            "config": self._config,
            })

        # Load config
        if autoload:
            config_file, content = self.read_config_file()
            if config_file:
                self.load_config(config_file, content)
                log.debug("Configuration after loading from file: %(config)s", {
                    "config": self._config,
                    })
            else:
                log.warn("Can't find config file - using defaults")


    @staticmethod
    def read_config_file():
        # Try loading file from some standard locations. First match is used.
        locations = [
            # /etc/
            "/etc",

            # Current working directory
            os.getcwd(),

            # CWD/etc/immunio.ini
            os.path.join(os.getcwd(), "etc/"),

            # homedir
            os.path.expanduser("~"),
        ]

        # Also try every location from CWD up to root '/'
        path = os.getcwd()  # This was already included above
        while True:
            new_path, _ = os.path.split(path)
            if new_path == path:
                # At root, we're done
                break
            locations.append(new_path)
            path = new_path

        # Find first matching config file.
        for location in locations:
            # Search config filenames - prefer new one
            for name in [CONFIG_FILENAME, CONFIG_LEGACY_FILENAME]:
                filename = os.path.join(location, name)
                log.debug("Trying to find config file at %(filename)s", {
                    "filename": filename,
                    })

                # Try to open the file to see if it exists. Avoids any race
                # conditions between checking existence and opening.
                try:
                    with open(filename, "rb") as f:
                        content = f.read()
                    log.debug("Found config file at %(filename)s", {
                        "filename": filename,
                        })
                    return filename, content
                except IOError as exc:
                    # re-raise all exceptions except file-not-found
                    if exc.errno != errno.ENOENT:
                        raise ConfigError(
                            "Error reading IMMUNIO config file '%s': %s" % (
                            filename, exc))
        # No config file found, return None
        return None, None

    def load_config(self, filename, content):
        if filename.endswith(".ini"):
            return self.load_ini_config(filename, content)
        elif filename.endswith(".json"):
            return self.load_json_config(filename, content)
        raise ValueError("Can't read from file with this extension: '%s'" % (
            filename,))

    def load_ini_config(self, filename, content):
        fp = io.BytesIO(content)
        parser = SafeConfigParser()
        parser.readfp(fp, filename)
        if parser.has_section(IMMUNIO_SECTION_NAME):
            self._config.update(dict(parser.items(IMMUNIO_SECTION_NAME)))

    def load_json_config(self, filename, content):
        try:
            self._config.update(json.loads(content))
        except (ValueError, EnvironmentError) as exc:
            raise ConfigError(
                "Error reading IMMUNIO config file '%s': %s" % (filename, exc))

    def get(self, name, default=None, datatype=None):
        """
        Get a config value. Precedence is first environment variable,
        then config file, then fall back to the default.
        """
        environ_name = "IMMUNIO_%s" % name.upper()

        if environ_name in os.environ:
            str_value = os.environ[environ_name]
        else:
            str_value = self._config.get(name, default)

        return convert(str_value, datatype)

    @property
    def agent_enabled(self):
        """
        Helper shortcut for testing if the agent is enabled.
        """
        return self.get("agent_enabled", default=True, datatype=bool)


def convert(value, datatype=None):
    """
    Convert a value to the specified datatype. If the value is already
    the correct type, just return it.
    """
    # If final value is None, return None
    if value is None:
        return None

    # Convert the data type if specified
    if datatype is int:
        return int(value)

    if datatype is bool:
        # If value is already a bool, just return it
        if isinstance(value, bool):
            return value
        # Convert string value to bool
        if value.lower() in ["t", "true", "y", "yes", "on", "1"]:
            return True
        elif value.lower() in ["f", "false", "n", "no", "off", "0"]:
            return False
        else:
            raise ValueError("Can't interpret `%s` as bool" % value)

    if datatype is set:
        # If value is already a set, just return it
        if isinstance(value, set):
            return value

        # If value is a list or tuple, just convert to a set
        if isinstance(value, list) or isinstance(value, tuple):
            return set(value)

        # Treat strings as comma-separated values.
        if isinstance(value, basestring):
            # Empty strings are empty sets
            if value.strip() == "":
                return set()
            parts = value.split(",")
            return set(x.strip() for x in parts)

        raise ValueError("Can't interpret `%s` as set" % value)


    # No conversion required
    return value
