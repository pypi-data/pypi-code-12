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

# Is it time to send the tweet
'''Is it time to send the tweet'''

# standard libraries imports
import datetime
import sys

class TimeToSend(object):
    '''TimeToSend class'''
    def __init__(self, cfgvalues):
        '''Constructor for the TimeToSend class'''
        self.weekdays = ['mon','tue','wed','thu','fri','sat','sun']
        self.translateweekdays = {0: 'mon',
                                    1: 'tue',
                                    2: 'wed',
                                    3: 'thu',
                                    4: 'fri',
                                    5: 'sat',
                                    6: 'sun'}
        self.dayhours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        activehours = [i for i in cfgvalues['hours'].split(',') if i != '']
        activedays = [i for i in cfgvalues['days'].split(',') if i != '']
        self.sendthesedays = []
        self.sendthesehours = []
        # get the days while sending tweets is authorized
        for day in activedays:
            if '-' in day:
                dstart, dend = day.split('-')
                gendays = (i for i in self.weekdays[self.weekdays.index(dstart):self.weekdays.index(dend)+1])
                for x in gendays: self.sendthesedays.append(x)
            else:
                self.sendthesedays.append(day)
        # get the hours while sending tweets is authorized
        for hour in activehours:
            if '-' in hour:
                hstart, hend = hour.split('-')
                for k in [hstart, hend]:
                    if int(k) < 0:
                        print('db2twitter.ini config file has a wrong value : hours should be >= 0')
                        sys.exit(0)
                    if int(k) > 23:
                        print('db2twitter.ini config file has a wrong value : hours should be <= 23')
                        sys.exit(0)
                genhours = (i for i in self.dayhours[self.dayhours.index(int(hstart)):self.dayhours.index(int(hend)+1)])
                for y in genhours:
                    self.sendthesehours.append(int(y))
            else:
                if int(hour) < 0:
                    print('db2twitter.ini config file has a wrong value : hours should be >= 0')
                    sys.exit(0)
                if int(hour) > 23:
                    print('db2twitter.ini config file has a wrong value : hours should be <= 23')
                    sys.exit(0)
                self.sendthesehours.append(int(hour))

    @property
    def sendthetweet(self):
        '''main of TimeToSend class'''
        #get the current date
        currentdate =  self.getdate()
        currentweekday = self.translateweekdays[currentdate.weekday()]
        currenthour = currentdate.hour
        isgoodday = False
        isgoodhour = False
        if currentweekday in self.sendthesedays:
            isgoodday = True
        if currenthour in self.sendthesehours:
            isgoodhour = True
        if isgoodday and isgoodhour:
            return True
        else:
            return False

    def getdate(sel):
        '''get the current date and time'''
        return datetime.datetime.now()

