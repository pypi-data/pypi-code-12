from __future__ import print_function

import logging
import json
import shlex
import psutil
import operator
import string
import re
import datetime
import time
import six
import sys

from operator import itemgetter

import okerrclient

class NoMethodException(Exception):
    pass

class BadMethodException(Exception):
    pass

class BadInputException(Exception):
    pass



#
# Taskprocessor is parent class for processor, which implements sequence code
# like 'DIR' or 'JDUMP'
#

class TaskProcessor:

    _help='help stub'
    code = '<No Code>'
    
    store_argline=None # if set, whole argline stored in this key in args{} dict
    store_cmdline=None # same, but with method
    parse_args=True # set False to not parse args. (e.g. if method has just one required arg)

    chapter = 'NO SPECIFIC CHAPTER'

    defargs={}
    tpconf={}


    #
    # TaskProcessor.run()
    #

    def run(self,ts,data,args):
        print('YOU MUST OVERRIDE RUN')
        return 123456
    
    @property   
    def help(self):
        return 'ZZZ' + self._help

    def fullhelp(self):
        
        msg = ""
        msg += self.code+'\t'+self.help+'\n'
        
        if self.tpconf:
            msg += '\tconfiguration:\n'
            for cname in sorted(self.tpconf):
                msg += '\t{}: {}\n'.format(cname,self.tpconf[cname])
            msg+='\n'
        
        if self.parse_args and self.defargs:                    
            msg += '\tArguments:\n';
            for aname in sorted(self.defargs):
                msg += '\t'+aname+'='+repr(self.defargs[aname])+'\n'
        if self.store_argline:
            msg+='\targument ({}), default: "{}"\n'.format(self.store_argline,self.defargs[self.store_argline])
        return msg
        
    def tpconfset(self,k,v):
        if k in self.tpconf and isinstance(self.tpconf[k],six.string_types):
            self.tpconf[k]=v
        elif k in self.tpconf and isinstance(self.tpconf[k],list):
            self.tpconf[k].append(v)
        else:
            self.tsclass.oc.log.error('Task Processor \'{}\' has no configuraton key \'{}\''.format(self.code,k))            
          

    def __init__(self, code, tsclass):
        self.code = code
        tsclass.addtproc(code,self)
   
    def parseargs(self, args):
        ad = dict(self.defargs) # copy default dictionary
        
        # set method
        ad['command']=self.code
        
        if self.parse_args:
            va = shlex.split(args)[1:]        
            for v in va:
                kv = v.split('=',1)                                
        
                if kv[0] in ad:                    
                    if len(kv)==2:
                        ad[kv[0]]=kv[1]
                    else:
                        ad[v]=None
                else:
                    self.tsclass.oc.log.error('bad argument: {}, try: okerr-client --help {}'.format(args, self.code))
                    sys.exit(1)

        if self.store_cmdline:
            ad[self.store_cmdline] = args
        if self.store_argline:
            if ' ' in args:
                ad[self.store_argline] = args.split(' ',1)[1]
        return ad

    def argbool(self,args,name):
        if not name in args:
            return False
        if args[name]=='0':
            return False
        return True
    
    
    

#
# route just array of text, like [ "KEYVAL", "JDUMP"]
#
#
#
    
class TaskSeq():
    oc = None # okerr client object
    iname = None # indicator
    method = None # method of indicator
    details = None # details

    tags=[]
    
    v = {}

    #methods={'OK': self.ok,'ERR': self.err, 'STR': self.string }
    tp={} # task processors

    parent = None

    _stop = False

    
    def stop(self):
        self._stop = True

    #
    # TaskSeq.mkargs
    #
    # convert element ('OK' or 'ANYCODE arg1..', or dict)
    # to route element
    # 
    def mkargs(self,s):
        if isinstance(s,six.string_types):
            try:
                m = shlex.split(s)[0]
            except ValueError:
                raise ValueError('Cannot parse command: {}'.format(s))
                return None
            #self.oc.log.debug('parsing command {}'.format(s))
            
            
            if not m in self.tp:
                raise NoMethodException('No method '+m)
                                   
            # MK ARGS
            args = self.tp[m].parseargs(s)
                                    
            #self.oc.log.debug('args: {}'.format(args))
            return args
            
        elif isinstance(s,dict):
            if not 'command' in s:
                raise ValueError
            if not s['command'] in self.tp:
                raise NoMethodException        
                
            # fill defargs
            code = s['command']
            for k in self.tp[code].defargs:
                if not k in s:
                    s[k]=self.tp[code].defargs[k]
            
            if self.tp[code].store_argline and 'argline' in s:
                s[self.tp[code].store_argline] = s['argline']
            
            return s    


    #
    # TaskSeq.setseq - set sequence   
    # seq is always list.
    # element is either string like 'OK' or 'ANYCODE arg1=val1 arg2=val2'
    # or element is dict with fields 'cmd' and argnames
    #

    def setseq(self,seq):
        
        route = list()
        
        for s in seq:            
            args = self.mkargs(s)            
            route.append(args)
    
    
        self.fullroute=list(route) # copy it
        self.route = list(route) # copy it
        self.checkroute()


    #
    # TaskSeq.__init__
    #

    def __init__(self,iname,route,method=None):
        self.iname = iname
        
        self.initvars()

        if route is not None:
            self.setseq(route)

        self.method=method
        self.tags=list()
        
        # print("created. iname:{}".format(iname))

    def initvars(self):
        pass
  

    #
    # TaskSeq.fork
    # 

    def fork(self,iname,route,method=None):
        ts = TaskSeq(iname,route,method)
        ts.iname = iname
        ts.oc = self.oc
        ts.method = self.method
        ts.details = self.details
        ts.parent = self
        ts.tags = list(self.tags)
        return ts


    def checkroute(self):
        for r in self.route:
            if not 'command' in r or not r['command'] in self.tp:
                raise NoMethodException("No method '{}'".format(m))

        return True

    def setvar(self,name,value):
        self.v[name]=value


    def getvar(self,name):
        if name in self.v:
            return self.v[name]
        return None


    def getvars(self):
       v = self.v.copy()
       v['_name']=self.iname
       return v
        
    def settag(self,tagname):
        if re.match('[a-zA-Z0-9_]*',tagname):
            self.tags.append(tagname)
        
    @classmethod
    def addtproc(cls, code, tproc):
        # check validity
        if isinstance(tproc,TaskProcessor):
            cls.tp[code]=tproc
            tproc.tsclass=cls
        else:
            # method is not child of TaskProcessor
            raise BadMethodException()
            
    @classmethod
    def help(cls):

        def helpchapter(chapters,chapter):
            msg='  '+chapter+'\n  ---\n'
            for c in sorted(chapters[chapter],key=operator.attrgetter('code')):
                msg+=c.fullhelp()
            msg+='\n'
            return msg

        
        chapters={}
        
        for code in cls.tp:
            c = cls.tp[code]
            
            if not c.chapter in chapters:
                chapters[c.chapter] = [c]
            else:
                chapters[c.chapter].append(c)

        msg='Available commands:\n\n'
        msg+=helpchapter(chapters,'General')
        for chapter in sorted(chapters):
            if chapter!='General':
                msg+=helpchapter(chapters,chapter)
            
        return msg
       
   #
   # TaskSeq.run
   #
   
    def run(self,data=None):
        # print("run ({}) {}".deformat(self.iname,self.route))

        def strcmd(r):
            arg=''
            for k,v in r.items():
                if k!='command':
                    arg+="{}={} ".format(k,v)    
            return "{} {}".format(r['command'],arg)
                   
        for r in self.fullroute:
            self.route.pop(0)
    
            if self._stop:
                self.oc.log.debug('sequence name:{} id:{} got stop signal'.format(self.iname, id(self)))
                return

            r = r.copy()

            cmd = r['command']
                                
            self.oc.log.debug('RUN {}'.format(strcmd(r)))
            
            vv = self.getvars()
            
            if isinstance(data,six.string_types):
                vv['_str'] = data
                           
            # replace vars
            for argname,argval in r.items():
                #print("replace arg {} = {}".format(argname, argval))
                #print(vv)
                newval = string.Template(argval).safe_substitute(vv)
                #print("newval: {}".format(newval))
                r[argname] = newval

            
            if not cmd in self.tp:
                raise NoMethodException                   
                        
            # RUN task processor
            data = self.tp[cmd].run(self,data,r)
            #self.oc.log.debug('output: {}'.format(data))
    
        # print('i: {}, data: {}'.format(self.iname,data))
        
        if self.iname is not None: 
            if data is not None:
                self.oc.update(self.iname,data,details=self.details,
                method=self.method,tags=self.tags,error=None)
            else:
                self.oc.log.info('do no update indicator {}, because data is None'.format(self.iname))
        else:

            self.oc.log.info('do not update indicator, because no indicator name')



class GenTaskProcessor(TaskProcessor):
    chapter='General'

class JSONTaskProcessor(TaskProcessor):
    chapter='JSON processing'

class FormatTaskProcessor(TaskProcessor):
    chapter='Formatting'


class TaskMyName(GenTaskProcessor):
    help = 'returns self name'
    def run(self,ts,data,args):
        return self.code
    
    @property
    def help(self):
        return 'returns {}'.format(self.code)

TaskMyName('OK',TaskSeq)
TaskMyName('ERR',TaskSeq)



class TaskSet(GenTaskProcessor):
    
    parse_args=False
    store_argline='set'
    
    defargs= { 'set': ''}
    
    help = 'Set variable'
    def run(self,ts,data,args):
        setshlex = shlex.shlex(args['set'])
        setshlex.whitespace += '='
        setshlex.whitespace_split = True
        setstat= list(setshlex)
        if len(setstat) !=2:
            ts.oc.log.error('Cannot parse SET statement: {} . Should be in form SET varname=value or varname="some value"'.format(args['set']))
            return None
        ts.setvar(setstat[0],setstat[1])
        
        return data
    
   
TaskSet('SET',TaskSeq)


class TaskExport(GenTaskProcessor):
    
    parse_args=False
    store_argline='exp'
    
    defargs= { 'exp': '' }
    
    help = 'Export data (string) or string element of dict (string) to sequence variable'
    def run(self,ts,data,args):
    
        kv = re.split('\s*=\s*',args['exp'])
        if len(kv)==1 and isinstance(data,six.string_types):
            # this is string
            ts.setvar(kv[0],data)
        elif len(kv)==2 and isinstance(data,dict) and kv[1] in data:
            ts.setvar(kv[0],data[kv[1]])
        else:
            ts.oc.log.error('export error. Exp: {}, Data: {}'.format(args['exp'],str(data)[:50]))
                                        
        return data
    
TaskExport('EXPORT',TaskSeq)





class TaskTag(GenTaskProcessor):
    
    parse_args=False
    store_argline='tag'
    
    defargs= { 'tag': ''}
    
    help = 'Set tag'
    def run(self,ts,data,args):
        ts.settag(args['tag'])        
        return data
    
TaskTag('TAG',TaskSeq)




class TaskVersion(GenTaskProcessor):
    help = 'returns client version: "{}"'.format(okerrclient.version)
    def run(self,ts,data,args):
        return okerrclient.version
    
TaskVersion('VERSION',TaskSeq)



class TaskStr(GenTaskProcessor):
    help = 'if str argument is set, returns str. Joins list by \n, otherwise returns str(data).'
 
    store_argline='str'
    parse_args=False

    defargs = {'str': ''}
    def run(self,ts,data,args):
        if args['str']:
            s = args['str']
        else:
            try:       
                s = "\n".join(data)
            except:
                s = str(data)
    
        # now, trim it
        # s = s.strip('\r\n\t ')
        return s

TaskStr('STR',TaskSeq)

class TaskMethod(GenTaskProcessor):
    help = 'set method for this sequence, e.g. "numerical maxlim=80"'
 
    store_argline='method'
    parse_args=False

    defargs = {'method': ''}
    def run(self,ts,data,args):
        #mw = args['method'].split(' ')
        mw = shlex.split(args['method'])
        mstr = '|'.join(mw)
        ts.method=mstr
        return data

TaskMethod('METHOD',TaskSeq)


class TaskName(GenTaskProcessor):
    help = 'set new name for this sequence, e.g. "$_name:testname"'
 
    store_argline='name'
    parse_args=False

    defargs = {'name': '$_name:noname'}
    def run(self,ts,data,args):
        vv = ts.getvars()
        if isinstance(data,dict):
            vv.update(data) 
        ts.oc.log.debug("NAME: {}".format(args['name']))                
        ts.iname = string.Template(args['name']).safe_substitute(vv)
        #ts.iname = args['name']
        
        return data

TaskName('NAME',TaskSeq)



class TaskDetails(GenTaskProcessor):
    help = 'Set details'

    store_argline='format'
    parse_args=False

    defargs = {
        'format': '',
    }

    def run(self,ts,data,args):
        outstr=''
                
        fmt=args['format']

        if data is None:
            ts.details = fmt
            return None # can return data. anyway it's None

        if fmt:
            if isinstance(data,dict):       
                etpl = string.Template(fmt)            
                ts.details = etpl.safe_substitute(data)            
            else:
                ts.details = fmt            
             
        else:
            ts.details = str(data)
        

        # return same data 
        return data
                
TaskDetails('DETAILS',TaskSeq)



class DefaultProc(GenTaskProcessor):
    help = 'Set default data if data is empty'

    store_argline='def'
    parse_args=False

    defargs = {
        'def': '',
    }

    def run(self,ts,data,args):
        if not data:
            try:
                data = json.loads(args['def'])
            except ValueError as e:
                ts.oc.log.error("{}: not valid default JSON: {}".format(self.code, args['def']))
                ts.stop()
                return None
                
        return data
                
DefaultProc('DEFAULT', TaskSeq)        


class TaskInt(GenTaskProcessor):
    help = 'throws away fractional part'
    def run(self,ts,data,args):
        if isinstance(data,str) or isinstance(data,float) or isinstance(data,int):
            return int(float(data))
        else:            
            return None

TaskInt('INT',TaskSeq)


class TaskNonZero(GenTaskProcessor):
    help = 'Returns OK if input is number higher then 0, or returns ERR otherwise'
    def run(self,ts,data,args):
        print("nonzero data:",data)
        try:
            if int(data)>0:
                return 'OK'
            else:
                return 'ERR'
        except ValueError:
            ts.oc.log.error('bad data for {}: {} (must be numerical)'.format(self.code, data))
            return 'ERR'

TaskNonZero('NONZERO',TaskSeq)

class TaskOkErrNot(GenTaskProcessor):
    help = 'Inverse input. Returns OK if input is ERR, and returns ERR otherwise'
    def run(self,ts,data,args):
        if data == 'ERR':
            return 'OK'
        return 'ERR'
        
TaskOkErrNot('OKERRNOT',TaskSeq)

class TaskNone(GenTaskProcessor):
    help = 'returns None. (indicator will not be updated)'
    def run(self,ts,data,args):
        return None
        
TaskNone('NONE',TaskSeq)

class TaskSort(GenTaskProcessor):
    help = 'sort words or lines or lists'
    defargs = {'num': '0', 'sep': ' ', 'empty': '0','field': ''}
        
    def run(self,ts,data,args):
        was_str=False
        sep = args['sep'].replace('\\n','\n')

        if data is None:
            raise BadInputException('attempt to SORT None data')
    
        # make sure we have list
        if isinstance(data,str):
            was_str=True
            data = data.split(sep)
        
        # delete(?) empty elements
        if not self.argbool(args,'empty'):
            data = list(filter(len,data))
            
        if self.argbool(args,'num'):
            try:
                data = sorted(data, key=float)        
            except ValueError:
                pass
        else:
            if args['field']:
                data = sorted(data,key=itemgetter(args['field']))
            else:
                data = sorted(data)

        if was_str:
            data = ' '.join(data)
        
        return data
        
TaskSort('SORT',TaskSeq)

class TaskDump(GenTaskProcessor):
    help = 'pass data as-is, and print to stdout'
    def run(self,ts,data,args):
        print(data)        
        return data
        
TaskDump('DUMP',TaskSeq)


class TaskSeqDump(GenTaskProcessor):
    help = 'pass data as-is, print sequence data to stdout'
    def run(self,ts,data,args):
        datadumplen=100
    
        print("Sequence ({}): {}".format(ts.iname,id(ts)))
        if ts.parent is None:
            print("no parent")
        else:
            print("Parent {}: {}".format(id(ts.parent),ts.parent.iname))
        print("details:",ts.details)
        print("method:",ts.method)
        print("tags:",ts.tags)
        print("variables:",json.dumps(ts.v, sort_keys=True, indent=4, separators=(',',': ')))
        if data is None:
            print("no data")
        else:
            datastr=str(data)
            if len(datastr)>datadumplen:
                print ("data ({}/{}): {} ...".format(datadumplen, len(datastr), datastr[:datadumplen]))
            else:
                print ("data: ({}): {}".format(len(datastr),datastr))
        print("\n")
            
        return data
        
TaskSeqDump('SEQDUMP',TaskSeq)

class TaskJSON(JSONTaskProcessor):              
    help = 'convert any data to JSON string'
    def run(self,ts,data,args):
        return json.dumps(data)
        
TaskJSON('JSON',TaskSeq)


class TaskFromJSON(JSONTaskProcessor):
    help = 'convert JSON string to data'
    def run(self,ts,data,args):
        try:
            data = json.loads(data)
        except ValueError:
            ts.oc.log.error('Try to json-decode non json data: {}'.format(data))
            msg = '{}: Try to decode non-JSON data'.format(self.code, data)
            raise BadInputException(msg)
            return None
        return data                
        
TaskFromJSON('FROMJSON',TaskSeq)



class TaskJSONDump(JSONTaskProcessor):
    help = 'dump data in pretty JSON format to stdout. (returns None)'
    def run(self,ts,data,args):
        print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        return data
        
TaskJSONDump('JDUMP',TaskSeq)

class TaskMkSeq(GenTaskProcessor):
    help = 'make sequence from JSON/keyval structure or string'
        
    def mkroute(self,ts,data):
        route = list()
        for k in sorted(data, key=int):
            e = data[k]
            #etpl = string.Template(e)            
            #e = etpl.safe_substitute(v)            
                        
            args = ts.mkargs(e)
                       
            cmd = args['command']
                                    
#            for defarg in ts.tp[cmd].defargs:
#                if not defarg in e:
#                    e[defarg]= ts.tp[cmd].defargs[defarg]
                   
            route.append(args)
        return route 
    
    def launch(self, ts, data,v=None):
        

        #name = string.Template(data['name']).safe_substitute(v)
        
        # name = data['name'].format(iname=ts.iname)

        # build route from data
        route = self.mkroute(ts,data)        
        
        ts.oc.log.debug("launch sequence: {}".format(str(route)))
        
        # add remaining route
        route.extend(ts.route)

        # print("route:",route)

        try:
            newts = okerrclient.taskseq.TaskSeq(ts.iname, None, ts.method)
            newts.setseq(route)
                        
        except okerrclient.taskseq.NoMethodException as e:
            print(e)
            sys.exit(1)
        
        newts.run()


        
    def run(self,ts,data,args,v=None):
    
        if data is None:
            ts.oc.log.debug('will not MKSEQ because data is None')
            return None
    
        if v is None:
            v=dict()
        
        def hasdict(d):
            for sdname,subdata in d.items():
                if isinstance(subdata,dict):
                    return True
            return False
            
        
        if hasdict(data):
            for sdname,subdata in data.items():
                if isinstance(subdata,str):
                    v[sdname]=subdata    
                                
            for sdname,subdata in data.items():
                if isinstance(subdata,dict):
                    self.run(ts, subdata, args, v)                  
        else:
            self.launch(ts,data,v)
        
        # stop this sequence
        ts.stop()
        return None
    
    
TaskMkSeq('MKSEQ', TaskSeq)


class TaskDateTime(GenTaskProcessor):
    help = 'Set date and time variables'

    defargs = {
        'prefix': '_',
        'offset': '0'
    }

    def run(self,ts,data,args):               
        moment = time.time()
        moment += int(args['offset'])
        m = datetime.datetime.fromtimestamp(moment)
        
        
        prefix = args['prefix']
        ts.setvar(prefix+'day', m.day)
        ts.setvar(prefix+'month', m.month)
        ts.setvar(prefix+'year', m.year) 

        ts.setvar(prefix+'dd',"%02d" % m.day)
        ts.setvar(prefix+'mm',"%02d" % m.month)
        ts.setvar(prefix+'yy',"%02d" % (m.year % 100 ))

        ts.setvar(prefix+'hour', m.hour)
        ts.setvar(prefix+'minute', m.minute)
        ts.setvar(prefix+'second', m.second) 

        ts.setvar(prefix+'HH',"%02d" % m.hour)
        ts.setvar(prefix+'MM',"%02d" % m.minute)
        ts.setvar(prefix+'SS',"%02d" % m.second)


        return data

TaskDateTime('DATETIME', TaskSeq)




class TaskKeyVal(GenTaskProcessor):
    help = 'Retrieve data from okerr key-val database'

    store_argline='path'
    parse_args=False

    defargs = {
        'path': '',
    }

    def run(self,ts,data,args):               
        #print ("get keyval data from path: {}".format(args['path']))
        #print("args:", args)
        data = ts.oc.keypath(args['path'])
    
        if data is None:
            ts.oc.log.error('Failed to get keyval. Maybe you forgot to create path \'{}\' in okerr web interface?'.format(args['path']))
            ts.stop()

        return data

TaskKeyVal('KEYVAL', TaskSeq)

class TaskSave(GenTaskProcessor):
    help = 'Save data to variable'

    store_argline='varname'
    parse_args=False

    defargs = {
        'varname': '',
    }

    def run(self,ts,data,args):               
        ts.setvar(args['varname'], data)    
        return data

TaskSave('SAVE', TaskSeq)

class TaskLoad(GenTaskProcessor):
    help = 'Load data from variable'

    store_argline='varname'
    parse_args=False

    defargs = {
        'varname': '',
    }

    def run(self,ts,data,args):               
        return ts.getvar(args['varname'])    

TaskLoad('LOAD', TaskSeq)

class TaskDHMS(FormatTaskProcessor):
    help = 'convert number of seconds to DHMS string e.g. (12d 2h)'

    #store_argline='varname'
    #parse_args=False

    defargs = {
        'num': '2',
        'field': '',
        'destfield': ''
    }

    @staticmethod
    def dhms_short(sec, sep=" ", num=2):
        out=""
        nn=0
        t={'d': 86400,'h': 3600,'m': 60,'s': 1}
        for k in sorted(t,key=t.__getitem__,reverse=True):
            if sec>t[k]:
                if nn == num:
                    break
                nn+=1
                n = int(sec/t[k])
                sec-=n*t[k]
                out+="%d%s%s" % (n,k,sep)
        return out.strip()
    

    def run(self,ts,data,args):
    
        if isinstance(data,list):
            return map(lambda d: self.run(ts,d,args), data)
            
        if isinstance(data,dict):
            field = args['field']                        
            if field:
                dst = args['destfield']
                if not dst:
                    dst = field
                sec = int(float(data[field]))
                data[dst] = TaskDHMS.dhms_short(sec, ' ', int(args['num']))
                return data                         
                   
                   
        sec = int(float(data)) # in case if data is string or fraction
        return TaskDHMS.dhms_short(sec,' ', int(args['num']))
        

TaskDHMS('DHMS', TaskSeq)



class TaskKMGT(FormatTaskProcessor):
    help = 'Convert number (e.g. size of file) to string with suffix (e.g. 12M)'

    defargs = {
        'frac': '10',
        'field': '',
        'destfield': ''
    }


    @staticmethod
    def kmgt_short(sz, frac=10):
        t={
            'K': pow(1024,1),
            'M': pow(1024,2),
            'G': pow(1024,3),
            'T': pow(1024,4),
            '': 1}
            
        for k in sorted(t,key=t.__getitem__,reverse=True):
            if sz>t[k]:
                n = int((float(sz)*frac / t[k]))/float(frac)
                return "{}{}".format(n,k)

    def run(self,ts,data,args):               

        if isinstance(data,list):
            return map(lambda d: self.run(ts,d,args), data)
            
        if isinstance(data,dict):
            field = args['field']                        
            if field:
                dst = args['destfield']
                if not dst:
                    dst = field
                sz = int(float(data[field]))
                data[dst] = TaskKMGT.kmgt_short(sz, int(args['frac']))
                return data                         

        sz = int(float(data)) # in case if data is string or fra
        return TaskKMGT.kmgt_short(sz,int(args['frac']))

TaskKMGT('KMGT', TaskSeq)







