try:
    from gevent import monkey
    monkey.patch_all()
except ImportError as e:
    pass

import bottle

from bottle import Bottle, run

from malibu.config import configuration
from malibu.util import log
from malibu.util.args import ArgumentParser

from rest_api import dsn


class RESTAPIManager(object):

    __instance = None

    @classmethod
    def get_instance(cls):

        return cls.__instance

    @classmethod
    def from_argv(cls):
        """ Creates a RESTAPIManager from argparser args.
        """

        args = ArgumentParser.from_argv()
        args.set_default_param_type(
            argsPARAM_LONG,
            argsOPTION_PARAMETERIZED)

        args.add_option_mapping('c', 'config')
        args.add_option_type('c', args.OPTION_PARAMETERIZED)
        args.add_option_description('c', 'See also: --config')

        args.add_option_type('config', args.OPTION_PARAMETERIZED)
        args.add_option_description('config', 'Path to config file.')

        args.parse()

        config_file = None
        try:
            config_file = args.options['config']
        except:
            config_file = "api.ini"

        config = None
        try:
            config.load(self.__config_file)
            return cls(config=config)
        except:
            raise  # XXX - Handle this properly.

    def __init__(self, config=None):
        """ __init__(self, config=None)

            Initializes variables for config, begins config read,
            launches the DSN driver and sets up logging. After all that,
            launches the bottle server.
        """

        self.__config = config
        self.__app = None
        self.__dsn = None
        self.__logger = None

        if not config:
            raise AttributeError('config parameter not provided!')

        RESTAPIManager.__instance = self

    def load_bottle(self):
        """ load_bottle(self)

            Loads the bottle server and stores it.
        """

        self.__app = Bottle()
        if self.__config.get_section("debug").get_bool("enabled", False):
            self.__app.catchall = False
            bottle.debug(True)

        return self.__app

    def load_dsn(self):
        """ load_dsn(self)

            Loads the DSN driver and stores it.
        """

        dsn_enable = self.__config.get_section("debug").get_bool("enabled", False)
        if not dsn_enable:
            return None

        dsn_config = self.__config.get_section("debug")
        dsn_class = dsn.load_dsn(dsn_config.get_string("dsn_type", "sentry"))
        if not dsn_class:
            return None

        self.__dsn = dsn_class(self.__app)
        self.__dsn.set_config(config=dsn_config)
        self.__dsn.install()

        return self.__dsn

    def load_logging(self):
        """ load_logging(self)

            Loads the logging driver and stores it.
        """

        logging_config = self.__config.get_section("logging")

        logging_inst = log.LoggingDriver.from_config(logging_config)
        self.__logger = logging_inst

        return logging_inst.get_logger(name="rest_api")

    def run_bottle(self):
        """ run_bottle(self)

            Actually runs the bottle server for the API.
        """

        if not self.__app:
            return Exception("Bottle server has not been instantiated.")

        bottle_config = self.__config.get_section("api")

        if self.__dsn:
            run(
                app=self.__dsn.get_bottle_wrapper() or self.__app,
                host=bottle_config.get_string("listen", "127.0.0.1"),
                port=bottle_config.get_int("port", 18040),
                quiet=bottle_config.get_bool("quiet", True),
                debug=bottle_config.get_bool("devmode", False),
                reloader=bottle_config.get_bool("devmode", False),
                server=bottle_config.get_string("backend", "gevent"))
            return

    @property
    def app(self):
        """ property app(self)

            Return app instance.
        """

        return self.__app

    @property
    def config(self):
        """ property config(self)

            Return config instance.
        """

        return self.__config

    @property
    def dsn(self):
        """ property dsn(self)

            Return DSN instance.
        """

        return self.__dsn

    @property
    def arg_parser(self):
        """ property arg_parser(self)

            Returns the argument parser instance.
        """

        return self.__args

