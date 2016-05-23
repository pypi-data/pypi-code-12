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

# Check the size of an image
'''Check the size of an image'''

# 3rd party libraries imports
from PIL import Image

class ImageSize(object):
    '''ImageSize class'''
    def __init__(self, imagepath):
        '''Constructor of the ImageSize class'''
        self.imagepath = imagepath
        self.iswidthok = False
        self.isheightok = False
        self.width = 0
        self.height = 0
        self.twittermin = 4
        self.twittermax = 8192
        self.imagesizeok = False
        self.main()

    def main(self):
        '''Main of ImageSize class'''
        with Image.open(self.imagepath) as im:
            self.width, self.height = im.size
        # control the width - should be >= 4 and <= 8192
        if self.width >= self.twittermin and self.width <= self.twittermax:
            self.iswidthok = True
        else:
            self.iswidthok = False
        # control the height - should be >= 4 and <= 8192
        if self.height >= self.twittermin and self.height <= self.twittermax:
            self.isheightok = True
        else:
            self.isheightok = False
        # prepare return value
        if self.iswidthok and self.isheightok:
            self.imagesizeok = True
        else:
            self.imagesizeok = False

    @property
    def sendtotwitter(self):
        '''Return boolean if image size is ok'''
        return self.imagesizeok
