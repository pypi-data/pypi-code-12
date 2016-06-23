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
from tspetl import ETLTool


class ApacheLogTool(ETLTool):
    def __init__(self):
        super(ApacheLogTool, self).__init__()

    @property
    def name(self):
        return 'apachelog'

    @property
    def help(self):
        return 'Parses apache logs for page status. (Future Release)'

    def add_parser(self, sub_parser):
        super(ApacheLogTool, self).add_parser(sub_parser)
        self._parser.add_argument('-f', '--file', dest='file_path', metavar="file_path", help="Path to file to import", required=False)
        self._parser.add_argument('-b', '--batch', dest='batch_count', metavar="batch_count",
                                  help="How measurements to send in each API call", required=False)

    def _handle_arguments(self, args):
        pass

    def run(self, args):
        self._handle_arguments(args)

