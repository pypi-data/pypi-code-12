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
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Main class
'''Main class'''

# standard libraries imports
import configparser
import os.path
import sys

# 3rd party libraries imports
from sqlalchemy import desc
import tweepy

# app libraries imports
from db2twitter.cliparse import CliParse
from db2twitter.confparse import ConfParse
from db2twitter.dbparse import DbParse
from db2twitter.senttweets import SentTweets
from db2twitter.twbuild import TwBuild
from db2twitter.twsend import TwSend
from db2twitter.getdblasttweets import GetDbLastTweets
from db2twitter.twresend import TwReSend

class Main(object):
    '''Main class'''
    def __init__(self):
        '''Constructor of the Main class'''
        self.main()

    def main(self):
        '''Main of the Main class'''
        # parse the command line
        cargs = CliParse()
        cliargs = cargs.args
        # read the configuration file
        cfgparse = ConfParse(cliargs.pathtoconf)
        cfgvalues = cfgparse.confvalues
        # get the connector to the database storing the already-sent tweets
        senttweets = SentTweets(cfgvalues)
        sqlitesession = senttweets.sqlitesession
        if cliargs.circle:
                dblasttweets = GetDbLastTweets(cfgvalues, sqlitesession)
                twresend = TwReSend(cfgvalues, cliargs, dblasttweets.lasttweets)
        else:
            # parse the database
            dbparse = DbParse(cfgvalues, sqlitesession)
            dbvalues = dbparse.dbvalues
            # prepare the tweet
            twbuild = TwBuild(cfgvalues, dbvalues[0])
            tweets = twbuild.readytotweet
            # send the tweet
            twsend = TwSend(cfgvalues, cliargs, tweets, sqlitesession, dbvalues)
