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


class DBTool(ETLTool):
    def __init__(self):

        self._name = None
        self._password = None
        self._database = None
        self._query = None

    @property
    def name(self):
        return 'db'

    @property
    def help(self):
        return 'Import data from a relational database (Future Release)'

    def add_parser(self, parser):
        self._parser = parser.add_parser(self.name, help=self.help)
        self._parser.add_argument('-u', '--user', metavar='name',
                                  help="name of the user to connect to the database")
        self._parser.add_argument('-p', '--password', metavar='password',
                                  help="password of the user to connect to the database")
        self._parser.add_argument('-d', '--database', metavar='db_name',
                                  help="database to extract data from")
        self._parser.add_argument('-q', '--query', metavar='sql_query',
                                  help="SQL query to use to extract data")

    def handle_arguments(self, args):

        if args.name is not None:
            self._name = args.name
        pass

    def run(self, sink):
        print("Import CSV")
