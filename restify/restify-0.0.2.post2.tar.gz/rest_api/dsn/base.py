import rest_api, malibu

from malibu.util import log


class BaseDSNDriver(object):
    """ This class represents a bare DSN driver.
        Full DSN management drivers should implement
        this class to install and configure a DSN client
        (such as Sentry's Raven).
    """

    CONFIG_SECTION = "debug"
    SITE_NAME = "rest-api"

    def __init__(self, app = None):

        self.__app = app
        self.__config = {}
        self.__client = None

        self.__logger = log.LoggingDriver.find_logger()

        self.__will_run = True
        self.__needs_keys = []

    def set_config(self, config = {}):
        """ set_config(self, config = {})

            Should be provided with a malibu configuration section
            instance to pull config variables from.

            With a Configuration instance, you should do the following:

              driver.set_config(config.get_section(driver.CONFIG_SECTION))
        """

        config_keys = ["enabled", "host", "protocol", "public_key",
                "secret_key"]

        for key in config_keys + self.__needs_keys:
            if not self.__will_run: break
            if key not in config:
                self.__logger.error(
                    " --> Missing config key: debug.{}".format(key))
                self.__will_run = False
                continue

        self.__config = config

    def get_config(self):
        """ get_config(self)

            Simply returns this object's configuration section.
        """

        return self.__config

    def get_client(self):
        """ get_client(self)

            Simply returns this object's DSN client instance.
        """

        return self.__client

    def get_app(self):
        """ get_app(self)

            Simply returns this object's app instance.
        """

        return self.__app

    def set_client(self, client = None):
        """ set_client(self)

            Allows subclasses to set the client instance.
        """

        self.__client = client

    def connect(self):
        """ connect(self)

            Connects the DSN client to the DSN.
        """

        pass

    def install(self):
        """ install(self)

            Installs the DSN object into the Bottle application to collect
            logs and do the forwarding.
        """

        if not self.__client or not self.__will_run: return False
        else: return True

    @property
    def enabled(self):
        """ property enabled(self)

            Represents the configured status of the DSN.
        """

        return self.__config.get_bool("enabled", True)

    @property
    def host(self):
        """ property host(self)

            Represents the address of the DSN host we will connect to.
        """

        return self.__config.get_string("host", "")

    @property
    def protocol(self):
        """ property protocol(self)

            Represents the connection protocol of the DSN client.
        """

        return self.__config.get_string("protocol", "http")

    @property
    def public_key(self):
        """ property public_key(self)

            Represents the configured public key for connecting
            to the DSN.
        """

        return self.__config.get_string("public_key", "")

    @property
    def secret_key(self):
        """ property secret_key(self)

            Represents the configured secret key for connecting
            to the DSN.
        """

        return self.__config.get_string("secret_key", "")

    @property
    def will_run(self):
        """ property will_run(self)

            Represents the value of __will_run
        """

        return self.__will_run
