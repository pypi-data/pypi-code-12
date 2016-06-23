import argparse
import sys
import logging

from messenger_sdk.config import Config


class Log:
    def __init__(self, config: Config):
        self._config = config

    @staticmethod
    def _get_log_level():
        parser = argparse.ArgumentParser(description='Log level settings.')
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        parser.add_argument("--log", help="log level", choices=valid_levels, default='warning')
        args = parser.parse_args()
        return getattr(logging, args.log.upper(), None)

    def start_logging(self):
        filename = './logs/' + self._config.get_parameter('app', 'LOG_FILE_NAME')
        logging.basicConfig(filename=filename, format='[%(asctime)s] %(levelname)s: %(message)s',
                            level=self._get_log_level())
        if self._config.get_bool_parameter('app', 'LOG_TO_TERMINAL'):
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
