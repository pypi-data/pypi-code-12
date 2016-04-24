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

from dsgnutils import utils as uT

class ListDiffException(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)  # pragma: no cover


class ListDiff(object):
    '''
        find the indexes in the original list that made it into your target
        list...  multiple indices referencing the same object will be farmed to
        the uq list first in the case of a ListDiff .. check fallout
    '''
    def __guardTrivial(self):
        ret=False
        if not (self.A or self.B):
            self.AMB=[]
            self.BMA=[]
            self.AUB=[]
            self.BUA=[]
            ret=True
        elif not self.A:
            self.AMB=[]
            self.BMA=[x for x in self.B]
            self.AUB=[]
            self.BUA=[]
            ret=True
        elif not self.B:
            self.AMB=[x for x in self.A]
            self.BMA=[]
            self.AUB=[]
            self.BUA=[]
            ret=True
        return ret
    def __runDiff(self):
        #=======PROCESS TRIVIAL CASES=========================================
        if self.__guardTrivial():
            return None
        #=======FACT: len(lsX)>1; DO THEY NEED KEYS?==========================
        readyToProceed=False
        hasKey1=True if (uT.isSimpleType(self.A[0]) or self.keyA) else False
        hasKey2=True if (uT.isSimpleType(self.B[0]) or self.keyB) else False
        if hasKey1 and hasKey2:
            readyToProceed=True
        if not readyToProceed and (hasKey1 or hasKey2):
            if type(self.A[0])==type(self.B[0]):
                self.keyA=self.keyA if self.keyA else self.keyB
                self.keyB=self.keyA
                readyToProceed=True
        if not readyToProceed:
            msg='MISSING KEY(S) FOR'
            msg=msg if self.keyA else msg+' self.A'
            msg=msg if self.keyB else msg+' self.B'
            raise ListDiffException(msg)
        #=======MAKE SURE LISTS ARE INDEPENDENTLY HOMOGENEOUS=================
        homo1=uT.isHomogenous(self.A,verbose=True)
        homo2=uT.isHomogenous(self.B,verbose=True)
        if not (homo1 and homo2):
            msg='FOUND NON-HOMOGENEOUS ITERABLES(S):'
            msg=msg if homo1 else msg+' self.A'
            msg=msg if homo2 else msg+' self.B'
            raise ListDiffException(msg)
        #=======SORT THEM ON THEIR 'KEY'======================================
        a=sorted(self.A,key=self.keyA)
        b=sorted(self.B,key=self.keyB)
        #=======RUN A DIFF====================================================
        aIdx=0
        bIdx=0
        aLen=len(a)
        bLen=len(b)
        aUq=[]
        bUq=[]
        while aIdx<aLen and bIdx<bLen:
            cA=a[aIdx] if None==self.keyA else self.keyA(a[aIdx])
            cB=b[bIdx] if None==self.keyB else self.keyB(b[bIdx])
            if cA<cB:
                aUq.append(a.pop(aIdx))
                aLen-=1
            elif cA==cB:
                aIdx+=1
                bIdx+=1
            else:
                bUq.append(b.pop(bIdx))
                bLen-=1
        while aIdx<aLen:
            aUq.append(a.pop(aIdx))
            aLen-=1
        while bIdx<bLen:
            bUq.append(b.pop(bIdx))
            bLen-=1
        #=======ASSIGN DIFF WITH UNION IN BOTH REPRESENTATIONS================
        self.AMB=aUq
        self.BMA=bUq
        self.AUB=a
        self.BUA=b
        #-------GET INDIXES FOR A LISTS----------------------------------------
        mA={}
        for x in self.A:
            mA[x]=[]
        for (i,x) in enumerate(self.A):
            mA[x].append(i)
        for x in self.AMB:
            self.AMB_idxs.append(mA[x].pop(0))
        for x in self.AUB:
            self.AUB_idxs.append(mA[x].pop(0))
        for x in list(mA.keys()):
            assert(not mA[x])
        #-------GET INDICES FOR B LISTS----------------------------------------
        mB={}
        for x in self.B:
            mB[x]=[]
        for (i,x) in enumerate(self.B):
            mB[x].append(i)
        for x in self.BMA:
            self.BMA_idxs.append(mB[x].pop(0))
        for x in self.BUA:
            self.BUA_idxs.append(mB[x].pop(0))
        for x in list(mB.keys()):
            assert(not mB[x])
        self.AUB_idxs.sort()
        self.BUA_idxs.sort()
        self.AMB_idxs.sort()
        self.BMA_idxs.sort()
    def __init__(self,l1,l2,k1=None,k2=None):
        self.A=[x for x in l1]
        self.B=[x for x in l2]
        self.keyA=k1
        self.keyB=k2
        self.AMB=None
        self.BMA=None
        self.AUB=None
        self.BUA=None
        self.AMB_idxs=[]
        self.BMA_idxs=[]
        self.AUB_idxs=[]
        self.BUA_idxs=[]
        self.__runDiff()
    def __str__(self):
        return uT.pJ(
            {
                'A':[str(x) for x in self.A],
                'B':[str(x) for x in self.B],
                'AMB':[str(x) for x in self.AMB],
                'BMA':[str(x) for x in self.BMA],
                'AUB (in A)':[str(x) for x in self.AUB],
                'BUA (in B)':[str(x) for x in self.BUA],
                'AMB --indices':[str(x) for x in self.AMB_idxs],
                'BMA --indices':[str(x) for x in self.BMA_idxs],
                'AUB (in A) --indices':[str(x) for x in self.AUB_idxs],
                'BUA (in B) --indices':[str(x) for x in self.BUA_idxs]
            }
        )

class SetDiff(ListDiff):
    def __init__(self,l1,l2,k1=None,k2=None):
        assert(uT.isSet(l1,k1))
        assert(uT.isSet(l2,k2))
        super(SetDiff,self).__init__(l1,l2,k1,k2)
        
if '__main__'==__name__:

    class Point(object):
        def __init__(self,x,y):
            self.x=x
            self.y=y
        def __str__(self):
            return uT.pJ({'x':self.x,'y':self.y})

    print('\n\n')

    a=[Point(1,1),Point(2,4),Point(3,8)]
    b=[Point(1,1),Point(2,4),Point(3,9)]

    ld=ListDiff(a,b,k1=lambda x:x.y)

    t=ld.AUB
    berp=[str(x) for x in t]
    print(berp)

    print(ld)
    print('\n\n\n\n')




