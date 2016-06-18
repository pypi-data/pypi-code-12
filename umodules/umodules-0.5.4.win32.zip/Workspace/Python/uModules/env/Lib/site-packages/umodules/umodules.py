import logging
import sys

import umodules.parser as parser
import umodules.project as project

from umodules.config import Config

__version__ = "0.5.1"
__copyright__ = "Copyright 2016, SpockerDotNet LLC"


def __get_logging_level():

    #   default logging level
    level = logging.WARNING

    #   check args for -v or --verbose
    for arg in sys.argv:
        if arg == '-v' or arg == '--verbose':
            level = logging.DEBUG

    return level


def __init__():

    #   setup logging
    logging.basicConfig(
        filename="./umodules.log",
        level=__get_logging_level(),
        format='[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    #   add console logging
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    #   reduce Yapsy logging
    logging.getLogger("yapsy").setLevel(logging.ERROR)

    #   some diagnostic info
    logging.debug(sys.path)

    #   a little welcome message
    logging.info("Welcome to uModules")
    logging.info(__version__)
    logging.info(__copyright__)


def main():
    try:
        #   initialize the command
        __init__()

        #   create config object
        config = Config()

        #   find all plugins
        config.load_plugins()

        #   get all module types plugins
        module_types = config.get_modules()

        #   get all command plugins
        commands = config.get_commands()

        # git.test()
        # test = TestModule()
        # test.init()

        #   add commands to the parser
        args = parser.create_parser(commands).parse_args()

        #   create the project from the project file
        proj = project.load(args.config)
        logging.debug(proj)

        #   set the available project module types
        proj.module_types = module_types

        #   execute command with project object
        args.func(proj)

        exit(0)

    except Exception as e:
        logging.error(e)
        exit(1)
