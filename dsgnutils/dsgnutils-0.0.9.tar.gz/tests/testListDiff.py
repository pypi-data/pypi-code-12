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

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises

from dsgnutils.utils import *
from dsgnutils.listDiff import *

from tests.testClasses import Point
from tests.testClasses import Point3D
from tests.testClasses import Gnarly

class Test_ListDiffAndFriends(object):

    def __init__(self):
        self.ls1=[3,2,1]
        self.ls2=[1,2,4]
        self.ls3=[5,4,3,2,1]
        self.ls4=[12,2,1]
        self.ls5=[1,2,4,8]
        self.ls6=[1,'a',1]
        self.ls7=[Point(1,1),Point(2,4),Point(3,9)]
        self.ls8=[Point3D(1,1,1),Point3D(2,4,16)]
        self.ls9=[Point(1,1),Point(1,2),Point(3,9)]

    def test_ListDiff_trivial1(self):
        eo=([],([],[]),[])
        ld=ListDiff([],[])
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)
    def test_ListDiff_trivial2(self):
        eo=(self.ls1,([],[]),[])
        ld=ListDiff(self.ls1,[])
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        print(vals)
        assert_equal(eo,vals)
    def test_ListDiff_trivial3(self):
        eo=([],([],[]),self.ls1)
        ld=ListDiff([],self.ls1)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)

    def test_ListDiff_sharedKey1(self):
        eo=([],(self.ls7,self.ls7),[])
        ld=ListDiff(self.ls7,self.ls7,k1=lambda x:x.y)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)
    def test_ListDiff_sharedKey2(self):
        eo=([],(self.ls7,self.ls7),[])
        ld=ListDiff(self.ls7,self.ls7,k2=lambda x:x.y)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)
    def test_ListDiff_keyFailure(self):
        assert_raises(
            ListDiffException,
            ListDiff,
            self.ls7,
            self.ls8,
            k1=lambda x:x.y
        )

    def test_ListDiff_nonHomogeneous1(self):
        assert_raises(ListDiffException,ListDiff,self.ls1,self.ls6)
    def test_ListDiff_nonHomogeneous2(self):
        assert_raises(ListDiffException,ListDiff,self.ls6,self.ls1)

    def test_ListDiff_simple1(self):
        eo=([3],([1,2],[1,2]),[4])
        ld=ListDiff(self.ls1,self.ls2)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)
    def test_ListDiff_simple2(self):
        eo=([3,5],([1,2,4],[1,2,4]),[])
        ld=ListDiff(self.ls3,self.ls2)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)
    def test_ListDiff_simple3(self):
        eo=([12],([1,2],[1,2]),[4,8])
        ld=ListDiff(self.ls4,self.ls5)
        vals=(ld.AMB,(ld.AUB,ld.BUA),ld.BMA)
        assert_equal(eo,vals)

    def test_ListDiff_objectKey(self):
        eo=[1,4]
        ld=ListDiff(self.ls2,self.ls7,k2=lambda x:x.y)
        assert_equal([1, 4],ld.AUB)

    def test_SetDiff_OK(self):
        a=[Point(1,1),Point(2,4),Point(3,8)]
        b=[Point(1,1),Point(2,4),Point(3,9)]
        ld=SetDiff(a,b,k1=lambda x:x.x)
        assert_equal([],ld.AMB)



    def test_isSimpleSequence_success(self):
        assert_equal(True,isSimpleSequence(self.ls8,k=lambda x:x.x))
    def test_isSimpleSequence_failure(self):
        assert_equal(False,isSimpleSequence(self.ls5))
 
if '__main__'==__name__:
    pass

