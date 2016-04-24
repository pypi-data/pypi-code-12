'''
Copyright 2015 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

from dsgnutils.always import *
import dsgnutils.utils as uT

class Point(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def __str__(self):
        return json.dumps({'x':self.x,'y':self.y},sort_keys=True)
    def pErrTest(self):
        uT.pErr('THIS IS A TEST.  THIS IS ONLY A TEST.',self)
        

class Point3D(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def __str__(self):
        return json.dumps({'x':self.x,'y':self.y,'z':self.z},sort_keys=True)

class Gnarly(Point3D):
    def __init__(self,x,y,z):
        super().__init__(x,y,z)
        self.ls=[self.x,self.y,self.z]

