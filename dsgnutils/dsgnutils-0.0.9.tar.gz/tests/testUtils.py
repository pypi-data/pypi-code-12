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

from dsgnutils.utils import *
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from tests.testClasses import Point
from tests.testClasses import Point3D
from tests.testClasses import Gnarly

class Test_printingFunctions(object):
    def test_pJ(self):
        dic={'x':1,'y':2}
        string='''{\n    "x": 1,\n    "y": 2\n}'''
        assert_equal(pJ(dic),string)
    def test_pJ2(self):
        eo='    {\n        "0": 1\n    }'
        assert_equal(eo,pJ({0:1},tabIdx=1))
    def test_mkBanner(self):
        tStr=charFill('A',99)
        eo='===============================================================================\n=======AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ...(truncd):====================\n===============================================================================\n'
        assert_equal(eo,mkBanner(tStr))

class Test_osFunctionality(object):
    maxDiff=None

    testdir='%s/tests/data/test_osFunctionality'%(os.getcwd())
    lockProg1='''
    '''
    lockProg2='''
    '''
    def __init__(self):
        self.testDir=Test_osFunctionality.testdir
    @classmethod
    def setup_class(cls):
        os.makedirs(Test_osFunctionality.testdir)
        with open('%s/prog1.py'%(Test_osFunctionality.testdir),'w') as f:
            f.write(Test_osFunctionality.lockProg1)
        with open('%s/prog2.py'%(Test_osFunctionality.testdir),'w') as f:
            f.write(Test_osFunctionality.lockProg2)
    @classmethod
    def teardown_class(cls):
        shutil.rmtree(Test_osFunctionality.testdir)
    def setup(self):
        pass
    def teardown(self):
        pass
    @raises(PermissionError)
    def test_getFile(self):
        getFile('/notadirectoryhopefully/bad.txt')
    def test_BashIOE_Legit(self):
        cmd='ls %s'%(shlex.quote(self.testDir))
        eo='prog1.py\nprog2.py\n'
        br=BashIOE(cmd)
        assert_equal(eo,br.dumpOut())
    def test_BashIOE_Injection_shlex_quote1(self):
        arg=shlex.quote(self.testDir+'; echo HAXXORZ')
        cmd='ls %s'%(arg)
        eoRe='^ls: cannot access .*$'
        br=BashIOE(cmd)
        match=False if None==re.match(eoRe,br.dumpErr()) else True
        assert_equal(True,match)
    def test_BashIOE_Timeout(self):
        cmd='sleep 2'
        assert_raises(subprocess.TimeoutExpired,BashIOE,cmd,timeout=1)
    def test_F_Lock_forked_child(self):
        assert_equal.__self__.maxDiff = None
        eo='''Child locking...
TRYING LOCK...
GOT LOCK.
Child locked...
Parent locking...
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
Parent process failed to lock
Parent unlocking...
Parent unlocked.
Parent locking...
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
TRYING LOCK...
[Errno 11] Resource temporarily unavailable
Parent process failed to lock
Parent unlocking...
Parent unlocked.
Child unlocking...
CLOSING LOCK...
CLOSED LOCK.
Child unlocked.'''
        #TRANSCENDING UNIT BOUNDARY CAUSE CAN'T CAPTURE stderr W/ Nose
        holdDur=0.5
        cmd=StringIO()
        cmd.write('venv/bin/python')
        cmd.write(' tests/subord/testF_Lock_multiProc1.py')
        cmd.write(' %s/testF_Lock.lock %s'%(self.testDir,holdDur))
        br=BashIOE(cmd.getvalue(),timeout=32)
        ls=[x for x in sorted(br.out+br.err) if x]
        ls=[x.split(':')[4] for x in ls]
        ls=[re.sub(r'^ ','',x) for x in ls]
        rslt='\n'.join(ls)
        assert_equal(eo,rslt)

    @raises(F_LockException)
    def test_F_Lock_relock(self):
        ex=None
        try:
            flGen=F_LockGen('test.lock')
            lock=flGen.getInstance()
            lock.lock()
            lock.lock()
        except F_LockException as e:
            ex=e
        finally:
            lock.unlock()
        if ex:
            raise(ex)
        
    def test_F_Lock_threading(self):
        timeout=0.5
        sleepDur=timeout/2.0
        parentLatency=timeout/2.0
        parentHoldTime=timeout/2.0
        childHoldTime=3*timeout
        def holder(flGen,holdtime):
            lock=flGen.getInstance()
            try:
                lock.lock()
                time.sleep(holdtime)
            except F_LockException as e:
                raise
            finally:
                lock.unlock()
        def cycle(flGen,holdtime):
            ret=False
            lock=flGen.getInstance()
            try:
                lock.lock()
                time.sleep(holdtime)
                ret=True
            except F_LockException as e:
                raise
            finally:
                lock.unlock()
            return ret
        fLockGen=F_LockGen(
            'test.lock',
            timeout=timeout,
            sleepDur=sleepDur,
            verbose=True
        )
        t=threading.Thread(target=holder,args=(fLockGen,childHoldTime,))
        t.start()
        time.sleep(parentLatency)
        for i in range(2):
            assert_raises(F_LockException,cycle,fLockGen,parentHoldTime)
        t.join()
        rslt=cycle(fLockGen,0)
        assert_equal(True,rslt)
        os.remove('test.lock')

    @raises(PermissionError)
    def test_F_Lock_EACCESS(self):
        flGen=F_LockGen('/test.lock')
        lock=flGen.getInstance()
        lock.lock()
        lock.unlock()
    
    def test_Flatten(self):
        assert_equal([1,2,3],flatten([[1,2],[3]]))

    def test_TimeStamp(self):
        t=datetime.datetime.utcnow()
        ts=TimeStamp()
        assert_equal(t.year,ts.utc.year)
        assert_equal(t.month,ts.utc.month)
        assert_equal(t.day,ts.utc.day)
        assert_equal(t.hour,ts.utc.hour)
        assert_equal(t.minute,ts.utc.minute)
        assert_equal(t.second,ts.utc.second)

    def test_epoch0(self):
        e0=epoch0()
        assert_equal('1970-01-01T00:00:00.000000+00:00',dtStr(e0))


if '__main__'==__name__:

    dic={}
    dic[0]=1
    print(pJ(dic,tabIdx=1))
    
    
