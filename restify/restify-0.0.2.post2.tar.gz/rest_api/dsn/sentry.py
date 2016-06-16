import malibu, raven

from raven.contrib.bottle import Sentry

from malibu import config
from malibu.util import log

from rest_api.dsn import base


class SentryDSNDriver(base.BaseDSNDriver):

    def __init__(self, app = None):

        base.BaseDSNDriver.__init__(self, app = app)

        self.__base = super(SentryDSNDriver, self)
        self.__wrapper = None
        self.__logger = log.LoggingDriver.find_logger()

        self.__needs_keys = ["path", "project_id"]

    def __build_dsn_url(self):
        """ __build_dsn_url(self)

            Takes the known components from the configuration
            and builds a functional DSN URL for using with Raven
            to connect to Sentry.

            A DSN URL is in the following format:

              {protocol}://{public_key}:{secret_key}@{host}/{path}{project_id}
        """

        path = self.path if len(self.path) > 1 and self.path is not "/" else ""

        components = {
                "protocol"   : self.__base.protocol,
                "public_key" : self.__base.public_key,
                "secret_key" : self.__base.secret_key,
                "host"       : self.__base.host,
                "path"       : path,
                "project_id" : self.project_id,
        }

        return "{protocol}://{public_key}:{secret_key}@{host}" \
               "/{path}{project_id}".format(**components)

    def set_config(self, config = {}):
        """ set_config(self)

            Wrapper for BaseDSNDriver.set_config() to connect the Sentry
            DSN client immediately after the config is verified.
        """

        self.__base.set_config(config = config)

        if len(self.__base.get_config()) > 0:
            self.__config = config

        if self.will_run:
            self.__url = self.__build_dsn_url()
            self.connect()

    def get_bottle_wrapper(self):
        """ get_bottle_wrapper(self)

            Returns the Sentry wrapper used to wrap the Bottle app
            for exception catching.
        """

        return self.__wrapper

    def connect(self):
        """ connect(self)

            Connects the DSN client to the DSN itself and returns the
            instance.
        """

        site_name = self.__base.SITE_NAME

        try:
            self.__client = raven.Client(
                    dsn = self.__url,
                    public_key = self.__base.public_key,
                    secret_key = self.__base.secret_key,
                    project = self.project_id,
                    site_name = site_name)
            self.__base.set_client(self.__client)
            masked = self.__url.replace(self.__base.secret_key, '****')
            self.__logger.info("Connected to Sentry DSN: %s." % (masked))
        except Exception as e:
            self.__will_run = False
            self.__logger.error(" --> Encountered Exception while connecting DSN:")
            self.__logger.error(" --> {}".format(e))
            return None

        return self.__client

    def install(self):
        """ install(self)

            Instantiates and installs the Raven DSN into the Bottle
            framework for error reporting to Sentry.
        """

        if not self.__base.install():
            return False

        try:
            self.__base.get_app().catchall = False
            self.__wrapper = Sentry(self.__base.get_app(), self.__client)
        except Exception as e:
            self.__logger.error(" --> Encountered Exception while installing DSN:")
            self.__logger.error(" --> {}".format(e))
            return False

        return True

    @property
    def client(self):
        """ property client(base)

            Represents the client instance that is stored
            somewhere between self and base because of 
            subclassing.
        """

        return self.__base.get_client()

    @property
    def path(self):
        """ property path(self)

            Represents the configured path to Sentry, if it
            is not located at the HTTP root.
        """

        return self.__config.get_string("path", "/")

    @property
    def project_id(self):
        """ property project_id(self)

            Represents the configured project id to log events 
            to in the DSN.
        """

        return self.__config.get_int("project_id", -1)

