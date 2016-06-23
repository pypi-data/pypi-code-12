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
import argparse
from tspetl import ApacheLogTool
from tspetl import DBTool
from tspetl import CSVTool
from tspetl import GitHubTool
from tspetl import JiraTool
from tspetl import LogTool
from tspetl import SalesForceTool
from tspetl import SNMPTool
from tspetl import StockTool
from tspetl import SysLogTool
from tspetl import TwitterTool
from tspetl import WeatherTool
from tspetl import XMLTool

from tspetl import APIDataSink


class TspEtlCli(object):

    def __init__(self):
        self._parser = None
        self._subparsers = None
        self._args = None

        self._tool_map = {}
        self._add_tool(ApacheLogTool())
        # self._add_tool(DBTool())
        self._add_tool(CSVTool())
        # self._add_tool(GitHubTool())
        # self._add_tool(JiraTool())
        self._add_tool(LogTool())
        # self._add_tool(SalesForceTool())
        # self._add_tool(SNMPTool())
        # self._add_tool(StockTool())
        # self._add_tool(SysLogTool())
        self._add_tool(TwitterTool())
        self._add_tool(WeatherTool())
        # self._add_tool(XMLTool())

    def _add_tool(self, tool):
        self._tool_map[tool.name] = tool

    def load_tools(self):
        """
        TODO Add capability to dynamically load the tools
        :return:
        """
        pass

    def _create_parser(self):
        self._parser = argparse.ArgumentParser(description="Tool to extract/transform/load into Pulse")
        self._subparsers = self._parser.add_subparsers(help='commands', dest='command_name')

        for key, tool in self._tool_map.iteritems():
            tool.add_parser(self._subparsers)

    def run(self):
        self._create_parser()
        args = self._parser.parse_args()
        tool = self._tool_map[args.command_name]
        sink = APIDataSink(api_host=tool.api_host, email=tool.email, api_token=tool.api_token)
        tool.handle_arguments(args)
        tool.run(sink)


def main():
    cli = TspEtlCli()
    cli.run()


if __name__ == '__main__':
    main()
