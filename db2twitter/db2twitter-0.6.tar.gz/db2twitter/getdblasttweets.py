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

# GetDbLastTweets class
'''GetDbLastTweets class'''

# standard libraries imports
import sys

# 3rd party libraries imports
from sqlalchemy import desc

# app libraries imports
from db2twitter.wasposted import WasPosted

class GetDbLastTweets(object):
    '''GetDbLastTweets class'''
    def __init__(self, cfgvalues, sqlitesession):
        '''Constructor of the GetDbLastTweets class'''
        self.sqlitesession = sqlitesession
        # the max last tweets we can resend
        self.twnb = int(cfgvalues['circlelasttwnb'])
        # the number of tweets we send this time
        self.twbatchnb = int(cfgvalues['circletwbatchnb'])
        self.storetweets = False
        self.tweetstoresend = []
        self.main()

    def main(self):
        '''Main of GetDbLastTweets class'''
        dbresults = self.sqlitesession.query(WasPosted).order_by(desc(WasPosted.twid)).limit(self.twnb)
        i = 0
        while self.twbatchnb != 0:
            row = dbresults[i]
            # search the last circled tweet
            if row.lastcircled:
                self.storetweets = True
                row.lastcircled = False
                self.sqlitesession.commit()
            else:
                if self.storetweets:
                    # tweets to resend
                    self.tweetstoresend.append({'data': row.tweet,'imagepath': row.tweetimage})
                    self.twbatchnb -= 1
                    if self.twbatchnb == 0:
                        row.lastcircled = True
                        self.sqlitesession.commit()
            # counter to loop the row of dbresults
            if i == (self.twnb - 1):
                # check if previous circle was found, if not begin from first element in the last tweets
                if not self.storetweets:
                    self.storetweets = True
                i = 0
            else:
                i += 1

    @property
    def lasttweets(self):
        '''Last tweets to send from the database'''
        return self.tweetstoresend
