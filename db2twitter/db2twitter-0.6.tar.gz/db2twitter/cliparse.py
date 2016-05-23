# -*- coding: utf-8 -*-
# Copyright © 2015-2016 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# CLI parsing
'''CLI parsing'''

# standard libraries imports
from argparse import ArgumentParser
import os.path
import sys

class CliParse(object):
    '''CliParse class'''
    def __init__(self):
        '''Constructor for the CliParse class'''
        self.epilog = 'For more information: https://db2twitter.readthedocs.io'
        self.description = 'db2twitter automatically extracts fields from your database, use them to feed a template of tweet and send the tweet'
        self.main()

    def main(self):
        '''main of CliParse class'''
        parser = ArgumentParser(prog='db2twitter',
                                description=self.description,
                                epilog=self.epilog)
        parser.add_argument('pathtoconf', metavar='FILE', type=str,
                           help='the path to the retweet configuration')
        parser.add_argument('-c', '--circle', action='store_true',
                           default=False, help='circling the last tweets')
        parser.add_argument('--dry-run', dest='dryrun', action='store_true',
                           default=False, help='simulate the execution, no tweet sent')
        self.cliargs = parser.parse_args()
        if not os.path.exists(self.cliargs.pathtoconf):
            sys.exit('the path you provided for db2twitter configuration file does not exist')
        if not os.path.isfile(self.cliargs.pathtoconf):
            sys.exit('the path you provided for db2twitter configuration is not a file')

    @property
    def args(self):
        '''return the cli arguments'''
        return self.cliargs
