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

#=======LOGGING LEVELS=========================================================
#SYSTEM IS UNUSABLE
LOGLEVEL_EMERG=0
#ACTION MUST BE TAKEN IMMEDIATELY
LOGLEVEL_ALERT=1
#CRITICAL CONDITIONS
LOGLEVEL_CRIT=2
#ERROR CONDITIONS
LOGLEVEL_ERR=3
#WARNING CONDITIONS
LOGLEVEL_WARNING=4
#NORMAL BUT SIGNIFICANT CONDITION
LOGLEVEL_NOTICE=5
#INFORMATIONAL
LOGLEVEL_INFO=6
#DEBUG-LEVEL MESSAGES
LOGLEVEL_DEBUG=7

#=======OS FUNCTIONALITY=======================================================
class BashIOE(object):
    def __init__(self,cmd,timeout=16):
        '''
            WARNING this is essentially trusted code, and as such can be
            EXTREMELY DANGEROUS!  Advice: (1) Do not let untrusted users
            construct commands directly.  (2) make sure you're doing 'server
            side' validation on any user inputs which you might use to
            construct the cmd argument, AND (3) running any such 'validated'
            arguments through the shlex.quote function to avoid shell
            injections!  C.f.: out unit test function test_injection in the
            unit test class Test_BashIOE for an example of how to use
            shlex.quote, and also read and understand:
            https://docs.python.org/3/library/subprocess.html#security-considerations
        '''
        self.cmd=cmd
        self.out=None
        self.err=None
        self.code=None
        self.timeout=timeout
        proc=subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            executable='/bin/bash',
            universal_newlines=True
        )
        try:
            out,err=proc.communicate(timeout=self.timeout)
            proc.wait()
            self.out=[] if None==out else [x for x in out.split('\n')]
            self.err=[] if None==err else [x for x in err.split('\n')]
            self.code=proc.returncode
        except subprocess.TimeoutExpired as e:
            proc.kill()
            pErr(e,self)
            raise
    def __str__(self):
        return '%s%s%s\n%s%s\n%s%s%s%s%s'%(
            mkBanner('BashIOE'),
            overLine('CMD',c='-'),
            self.cmd,
            overLine('RET',c='-'),
            self.code,
            overLine('OUT',c='-'),
            self.dumpOut(),
            overLine('ERR',c='-'),
            self.dumpErr(),
            theLine
        )
    def dumpOut(self):
        return '\n'.join(self.out)
    def dumpErr(self):
        return '\n'.join(self.err)

def getFile(filename):
    ret=filename
    try:
        if not os.path.isfile(ret):
            path=os.path.dirname(ret)
            if path and not os.path.exists(path):
                os.makedirs(path)
        with open(ret,'a') as f:
            pass
    except PermissionError as e:
        pErr(e)
        raise
    return ret

class F_LockException(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value) # pragma: no cover

class F_Lock():
    '''
        WARNING: Do not construct this directly.  Use F_LockGen.getInstance()
        to acquire a new F_Lock object inside your critical section to get a
        new file descriptor which can then be locked and unlocked.  This
        prevents a loser thread from unlocking the the file descriptor of the
        winner thread.
    '''
    def __init__(self,fNom,timeout=64,sleepDur=1,verbose=False):
        self.fNom=fNom
        self.fd=None
        self.timeout=timeout
        self.sleepDur=sleepDur
        self.verbose=verbose
    def lock(self,timeout=None):
        timeout=timeout if timeout else self.timeout
        nao=datetime.datetime.now()
        if None!=self.fd:
            raise F_LockException(
                '%s HAS ALREADY LOCKED %s'%(
                    threading.current_thread(),
                    self.fNom
                )
            )
        fd=None
        while (datetime.datetime.now()-nao).total_seconds()<timeout:
            try:
                fd=open(self.fNom,"w+")
                if self.verbose:
                    pErr('TRYING LOCK...',self)
                fcntl.flock(fd.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
                if self.verbose:
                    pErr('GOT LOCK.',self)
                self.fd=fd
                break
            except Exception as e:
                self.unlock()
                if e.errno in [errno.EAGAIN]:
                    if self.verbose:
                        pErr(e,self)
                    time.sleep(self.sleepDur)
                else:
                    pErr(e,self)
                    raise
        if not self.fd:
            raise F_LockException(
                'FAILED TO ACQUIRE LOCK ON %s IN %s SECONDS'%(
                    self.fNom,
                    self.timeout
                )
            )
    def unlock(self):
        if None!=self.fd:
            if self.verbose:
                pErr('CLOSING LOCK...',self)
            self.fd.close()
            self.fd=None
            if self.verbose:
                pErr('CLOSED LOCK.',self)

class F_LockGen():
    '''
        Note that f_LockGen provides 
        document caveats; problems -- draft:
        --  if you're locking over NFS this can be bad if NFS version and or
            kernel version < x.y.z
        --  if cooperating independent programs (e.g. some bash script) dont
            use fcntl under the hood not sure what hapens
    '''
    def __init__(self,fNom,timeout=64,sleepDur=1,verbose=False):
        self.fNom=getFile(fNom)
        self.timeout=timeout
        self.sleepDur=sleepDur
        self.verbose=verbose
    def getInstance(self):
        return F_Lock(
            self.fNom,
            timeout=self.timeout,
            sleepDur=self.sleepDur,
            verbose=self.verbose
        )
        
        

#=======TYPE HACKS=============================================================
g__simpleTypes=[
    True,
    0,
    0.0,
    'c',
    'test',
    u'test',
]
g__simpleTypes=set([type(x) for x in g__simpleTypes])

def isSimpleType(x):
    return type(x) in g__simpleTypes

#=======LIST PROCESSING========================================================
def isHomogenous(ls,verbose=False):
    ret=True
    if 0<len(ls):
        ty=type(ls[0])
        for (i,x) in enumerate(ls):
            if ty!=type(x):
                ret=False
                if verbose:
                    pErr(
                        '(idx%s:%s; idx%s:%s)'%(
                            i,
                            type(ls[i]),
                            i+1,
                            type(ls[i+1])
                        )
                    )
                break
    return ret

def isSet(ls,k=None):
    L=[x for x in ls] if None==k else [k(x) for x in ls]
    S=set(L)
    return len(L)==len(S)

def isSimpleSequence(arg,k=None):
    '''keys on integer list types'''
    ret=True
    ls=sorted(arg,key=k)
    if 1<len(ls):
        for (i,_) in enumerate(ls[:-1]):
            cur=ls[i] if k==None else k(ls[i])
            nxt=ls[i+1] if k==None else k(ls[i+1])
            if 1!=nxt-cur:
                ret=False
                break
    return ret

def flatten(ls):
    return functools.reduce(operator.add,ls)

#=======PRINTING FUNCTIONS=====================================================
g__pep8LineLen=80
g__tabWidth=4

def charFill(c,n):
    ret=io.StringIO()
    for i in range(1,n):
        ret.write(str(c))
    return ret.getvalue()

def overLine(arg,c='=',n=g__pep8LineLen,lead=7,tailRatio=3):
    permittedLen=n-((tailRatio+1)*lead)
    msg=(str(arg)).upper()+':'
    if permittedLen<len(msg):
        infoStr=' ...(truncd):'
        msg=msg[:permittedLen-len(infoStr)]+infoStr
    return '%s%s%s\n'%(
        charFill(c,lead+1),
        msg,
        charFill(c,n-(lead+len(msg)))
    )

theLine=charFill('=',g__pep8LineLen)+'\n'

def mkHeader(arg):
    return overLine(arg,'=',g__pep8LineLen,7,3)

def mkBanner(arg):
    return "%s%s%s"%(theLine,mkHeader(arg),theLine)

def pErr(payload,obj=None):
    '''TOTAL WIP'''
    callerInfo=inspect.getframeinfo(inspect.currentframe().f_back)
    culprit=(type(obj).__name__)
    if 'NoneType'==culprit:
        culprit=callerInfo.filename
    behavior='%s()'%(callerInfo.function)
    if '<module>()'==behavior:
        behavior='%s'%(callerInfo.lineno)
    print(
        '[%s %s@%s]: %s'%(
            (TimeStamp()).loc(),
            culprit,
            behavior,
            payload
        ),
        file=sys.stderr
    )

def pJ(arg,sort=True,tabIdx=None):
    ret=json.dumps(arg,indent=4,sort_keys=sort,default=json_util.default)
    if None!=tabIdx:
        ret=ret.split('\n')
        pre=charFill(' ',tabIdx*g__tabWidth+1)
        for (i,x) in enumerate(ret):
            ret[i]='%s%s'%(pre,x)
        ret='\n'.join(ret)
    return ret



def pObj(obj,nom=None,rcrsDepth=3):
    '''
        Reduce the problem of printing objects to printing json.
    '''
    dic={}
    lNom=''
    if None!=nom:
        lNom+='%s '%(nom)
    lNom+='(%s):'%(type(obj).__name__)
    dic[lNom]=vars(obj)
    return pJ(dic)

def massageMultiline(arg,delim='\n',tabIdx=0):
    '''
        assumes you want to trim whitespace incl empty lines
    '''
    #TODO: should this not merge with lines to list core?
    ret=delim.join([x.strip() for x in arg.split('\n') if x])
    return ret

'''

{
    "util0":[
        {
            "username":"user0",
            "count":4
        },
        {
            "username":"user1",
            "count":2
        },
        {
            "username":"user4",
            "count":8
        }
    ]
}

'''

##=======FILE HANDLING=========================================================
class UsageTracker():
    def __init__(self,trackFile,lockFile):
        self.tracker=trackFile
        self.fLockGen=F_LockGen(lockFile)
        if not os.path.isfile(self.tracker):
            lock=self.fLockGen.getInstance()
            lock.lock()
            with open(getFile(self.tracker),'w') as f:
                f.write("{}")
            lock.unlock()
    def addEntry(self,utility,username):
        lock=self.fLockGen.getInstance()
        lock.lock()
        dic=readJson(self.tracker)
        if utility not in keys(dic):
            dic[utility]=[]
        uLs=dic[utility]
        u=None
        for (i,x) in enumerate(uLs):
            if x['username']==username:
                u=uLs.pop(i)
                break
        if None==u:
            u={"username":username,"count":0}
        u["count"]+=1
        uLs.append(u)
        uLs.sort(key=lambda x:x['username'])
        dic[utility]=uLs
        writeJson(dic,self.tracker)
        lock.unlock()
    def report(self):
        ret=None
        lock=self.fLockGen.getInstance()
        lock.lock()
        ret=readJson(self.tracker)
        lock.unlock()
        return pJ(ret)


#class LogParser():
#    pass
#
def readCSV(fNom,delim=','):
    ret=[]
    with open(fNom,'r') as f:
        c=csv.reader(f,delimiter=delim)
        for x in c:
            ret.append(x)
    return ret

def writeCSV():
    pass

def readJson(fNom):
    dic=None
    with open(fNom,'r') as f:
        dic=json.load(f)
    return dic

def writeJson(dic,fNom):
    s=pJ(dic)
    with open(fNom,'w') as f:
        f.write(s)

def readLines(fNom):
    lines=None
    with open(fNom,'r') as f:
        lines=f.read()
    lines=re.sub('\r\n','\n',lines)
    return lines.split('\n')

def writeLines(ls,fNom):
    with open(fNom,'w') as f:
        f.write('\n'.join(ls))

#=======EARTH SURFACE TIME=====================================================
def epoch0():
    return datetime.datetime(1970,1,1,0,0,0,tzinfo=pytz.utc)

def dtStr(dt):
    tz=dt.strftime('%z')
    tz='%s:%s'%(tz[0:3],tz[3:5])
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')+tz

def utcNow():
    t=datetime.datetime.utcnow()
    return datetime.datetime(
        t.year,
        t.month,
        t.day,
        t.hour,
        t.minute,
        t.second,
        t.microsecond,
        tzinfo=pytz.utc
    )

class TimeStamp(object):
    def __init__(self):
        self.utc=utcNow()
        sysTz=tzlocal.get_localzone()
        self.sys=sysTz.normalize(self.utc.astimezone(sysTz))
        assert(self.utc==pytz.utc.normalize(self.sys.astimezone(pytz.utc)))
    def __str__(self):
        return dtStr(self.utc)
    def loc(self):
        return dtStr(self.sys)



#=======DICTIONARY HELPERS=====================================================

def keys(arg):
    assert(type({})==type(arg))
    return list(arg.keys())



