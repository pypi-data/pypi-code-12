# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for upgrading ncloud.
"""
import logging
import pip
import requests
import sys

from ncloud.commands.command import Command
from ncloud.config import UPGRADE_URL


logger = logging.getLogger()


class Upgrade(Command):
    @classmethod
    def parser(cls, subparser):
        upgrade = subparser.add_parser("upgrade",
                                       help="Upgrade ncloud to the latest "
                                            "version.")
        upgrade.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(conf):
        try:
            res = requests.get(UPGRADE_URL)
        except requests.exceptions.RequestException as re:
            logger.error(re)
            sys.exit(1)

        package_path = res.text.strip()
        pip.main(['install', '--upgrade', package_path])
