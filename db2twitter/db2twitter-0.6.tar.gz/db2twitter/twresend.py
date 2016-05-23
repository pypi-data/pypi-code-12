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

# Send the tweet
'''Send the tweet'''

# 3rd party libraries imports
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import tweepy

# app libraries imports
from db2twitter.wasposted import WasPosted
from db2twitter.timetosend import TimeToSend

class TwReSend(object):
    '''TwReSend class'''
    def __init__(self, cfgvalues, cliargs, tweets):
        '''Constructor for the TwReSend class'''
        self.cfgvalues = cfgvalues
        self.cliargs = cliargs
        self.tweets = tweets
        # activate the twitter api
        self.auth = tweepy.OAuthHandler(self.cfgvalues['consumer_key'],
                                        self.cfgvalues['consumer_secret'])
        self.auth.secure = True
        self.auth.set_access_token(self.cfgvalues['access_token'],
                                    self.cfgvalues['access_token_secret'])
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.main()

    def main(self):
        '''main of TwSend class'''
        for tweet in self.tweets:
            if not tweet['imagepath'] or self.cfgvalues['circlenoimage']:
                if self.cliargs.dryrun:
                    print(tweet['data'])
                else:
                    self.api.update_status(status=tweet['data'])
            else:
                if self.cliargs.dryrun:
                    print('{} | image:{}'.format(tweet['data'], tweet['imagepath']))
                else:
                    self.api.update_with_media(tweet['imagepath'], status=tweet['data'])
