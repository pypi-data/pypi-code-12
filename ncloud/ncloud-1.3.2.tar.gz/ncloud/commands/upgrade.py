# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
