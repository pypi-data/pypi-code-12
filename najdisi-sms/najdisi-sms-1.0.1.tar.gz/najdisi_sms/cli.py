from argparse import ArgumentParser
import os
import sys

from six.moves.configparser import ConfigParser

import utils
from .api import SMSSender

log = utils.get_logger()


class SettingParser(object):
    """docstring for SettingParser"""
    def __init__(self, args=None):
        self.args = args or sys.argv[1:]

        home = os.path.expanduser('~')
        self.default_config_path = os.path.join(
            home,
            '.config',
            'najdisi_sms.ini'
        )

        self.argparser = self._create_argparser()
        self.parser_space = self.argparser.parse_args(self.args)

        self.namespace = self.merge_settings(self.parser_space)
        self.check_password_username(self.namespace)

    def _create_argparser(self):
        parser = ArgumentParser()
        parser.add_argument(
            "rec_num",
            metavar=u"reciever_NUM",
            help="slovenian phone number starting with 0"
        )
        parser.add_argument(
            "message",
            metavar=u"MESSAGE",
            help="SMS message (less than 160 characters)"
        )
        parser.add_argument(
            "-c",
            "--configfile",
            dest="config",
            help=u"Config file",
            default=self.default_config_path
        )
        parser.add_argument(
            "-u",
            "--username",
            dest="username",
            help=u"Username"
        )
        parser.add_argument(
            "-p",
            "--password",
            dest="password",
            help=u"Password"
        )
        parser.add_argument(
            "-A",
            "--useragent",
            dest="useragent",
            help=u"HTTP User Agent",
            default=("Mozilla/5.0 "
                     "(Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3)"
                     "Gecko/20100401 Firefox/3.6.3")
        )
        return parser

    def merge_settings(self, parser_space):
        """
        Merge config file and cli options
        """

        def parse_ini(file_path):
            config = ConfigParser()
            config.read(file_path)
            return config

        if os.path.exists(parser_space.config):
            ini_config = parse_ini(parser_space.config)
            for attr in ['username', 'password']:
                setattr(
                    parser_space,
                    attr,
                    getattr(parser_space, attr, None) or
                    ini_config.get('najdisi_sms', attr)
                )
        elif not self.default_config_path == parser_space.config:
            log.info('Config file you specified not found!')

        return parser_space

    def check_password_username(self, namespace):
        for attr in ['username', 'password']:
            if not getattr(namespace, attr):
                raise LookupError("Missing {}!".format(attr))


def main():
    parser = SettingParser()
    namespace = parser.namespace

    sender = SMSSender(
        namespace.username,
        namespace.password,
        namespace.useragent
    )
    sender.send(namespace.rec_num, namespace.message)


if __name__ == '__main__':
    main()
