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

# Build the tweet to send
'''Build the tweet to send'''

# standard libraries imports
import os.path

# app libraries imports
from db2twitter.imagesize import ImageSize

class TwBuild(object):
    '''TwBuild class'''
    def __init__(self, cfgvalues, dbvalues):
        '''Constructor for the TwBuild class'''
        self.cfgvalues = cfgvalues
        self.dbvalues = dbvalues
        self.tweets = []
        self.main()

    def main(self):
        '''main of TwBuild class'''
        # get hashtags
        if self.cfgvalues['hashtags'] != '':
            hashtags = self.cfgvalues['hashtags'].split(',')
            hashtags = [i for i in hashtags if i != '']
        for i in self.dbvalues:
            iswithimage = True
            if i['withimage']:
                # the tweet uses an image
                image = i['data'][-1]
                # lets apply a specific prefix to the image
                if self.cfgvalues['imageprefix']:
                    image = ''.join([self.cfgvalues['imageprefix'], image])
                # lets apply a specific path to the image
                if self.cfgvalues['imagepath']:
                    image = os.path.join(self.cfgvalues['imagepath'], image)
                # if the image path does not exist, fallback to no-image tweet
                if not image or not os.path.exists(image) or not os.path.isfile(image):
                    iswithimage = False
                else:
                    im = ImageSize(image)
                    if not im.sendtotwitter:
                        # try the fallback
                        if not self.cfgvalues['fallbackimageprefix']:
                            iswithimage = False
                        else:
                            fallbackimage = os.path.join(os.path.dirname(image), ''.join([self.cfgvalues['fallbackimageprefix'], os.path.basename(image)]))
                            # give up if the file of the fallback image does not exist
                            if not os.path.exists(fallbackimage):
                                iswithimage = False
                            else:
                                # check the size of the fallback image
                                fallback = ImageSize(fallbackimage)
                                if not fallback.sendtotwitter:
                                    iswithimage = False
                                else:
                                    image = fallbackimage
                if iswithimage:
                    j = self.cfgvalues['tweet'].format(*i['data'])
                    # identify and replace hashtags
                    j = j.lower()
                    for hashtag in hashtags:
                        pattern = ' ' + hashtag
                        if pattern in j.lower():
                            j = j.replace(pattern, ' #{}'.format(hashtag))
                    # uppercase for the first letter of the tweet
                    if self.cfgvalues['upper_first_char']:
                        j = j[0].upper() + j[1:]
                    self.tweets.append({'withimage': True, 'data': j, 'imagepath': image})
            if not i['withimage'] or not iswithimage:
                j = self.cfgvalues['tweet'].format(*i['data'])
                # identify and replace hashtags
                j = j.lower()
                for hashtag in hashtags:
                    pattern = ' ' + hashtag
                    if pattern in j.lower():
                        j = j.replace(pattern, ' #{}'.format(hashtag))
                # uppercase for the first letter of the tweet
                if self.cfgvalues['upper_first_char']:
                    j = j[0].upper() + j[1:]
                self.tweets.append({'withimage': False, 'data': j})

    @property
    def readytotweet(self):
        '''return the tweet ready to be sent'''
        return self.tweets
