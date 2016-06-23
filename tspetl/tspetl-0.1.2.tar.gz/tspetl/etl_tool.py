#
# Copyright 2016 BMC Software, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os


class ETLCollector(object):

    def __init__(self, sink):
        self._sink = sink

    def collect(self):
        pass


class ETLTool(object):

    def __init__(self):
        self._parser = None
        self._email = None
        self._api_token = None
        self._api_host = None

    @property
    def name(self):
        return None

    @property
    def help(self):
        return None

    @property
    def email(self):
        return self._email

    @property
    def api_token(self):
        return self._api_token

    @property
    def api_host(self):
        return self._api_host

    def add_parser(self, sub_parser):
        self._parser = sub_parser.add_parser(self.name, help=self.help)
        self._parser.add_argument('-e', '--e-mail', dest='email', metavar='email')
        self._parser.add_argument('-t', '--api-token', dest='api_token', metavar='token')
        self._parser.add_argument('-a', '--api-host', dest='api_host', metavar='hostname')
        self._parser.add_argument('-s', '--sink-type', dest='sink_type', choices=['api', 'rpc', 'std'])

    def handle_arguments(self, args):
        """
        Handled the command line arguments for the tool
        :param args: Namespace object from argparse
        :return: None
        """

        if args.email is not None:
            self._email = args.email

        if args.api_token is not None:
            self._api_token = args.api_token

        if args.api_host is not None:
            self._api_host = args.api_host

    def run(self, sink):
        pass
