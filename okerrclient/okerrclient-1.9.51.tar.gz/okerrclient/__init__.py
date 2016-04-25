#!/usr/bin/python

import requests
import sys
import os
import psutil
import time
import hashlib
import json

import logging
import logging.handlers

import evalidate

import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

version='1.9.51 (details)'


# TODO
# load/save caches
# methods (e.g. portlist)
# --prefix


class OkerrClient:

    # TODO: implement list of caches including ~/.okerr-cache.json
    cachepath = '/usr/local/etc/okerr-cache.json'
    url = 'http://update.okerr.com/okerr'
    textid = None
    secret = None
    log = None
    cache = None   
    prefix = None    
        
    cfgvars = ['secret','textid','url','keyuser','keypass','cachepath']
    
    def __init__(self,cfg=None):
        #print("init with cfg:",cfg)
        # default null log handler
        self.log = logging.getLogger()
        self.log.addHandler(logging.NullHandler())
        if cfg:            
            for k in self.cfgvars:
                if k in cfg:
                    #print("set self.{} to {}".format(k,cfg[k]))
                    setattr(self,k,cfg[k])
                else:
                    setattr(self,k,None)
    
    
    def __str__(self):
        return ("OkerrClient object\n"
            "cache: {cachepath}\n" 
            "url: {url}\n" 
            "textid: {textid}\n"
            "secret: {secret}\n").format(
                cachepath=self.cachepath,
                url=self.url, 
                textid=self.textid, 
                secret=self.secret)    

    def load(self):
        self.loadcache()

    def loadcache(self, force=False):
    
        self.cache={}
        return
    
        # load cache if it's not loaded
        # init/load cache
        try:
            with open(os.path.expanduser(self.cachepath),"r") as f:
                cachejson = f.read()
                self.cache = json.loads(cachejson)
        except IOError:
            self.log.info('no cache, initialize')
            self.cache={}
        except ValueError as e:
            self.log.error('broken cache: {}, reinit'.format(e))
            self.cache={}

    
    def save(self):
        self.savecache()
            
    def savecache(self):

        return
        
        self.cache['saved']=time.time()
       
        try: 
            with open(os.path.expanduser(self.cachepath),"w") as f:
                cachejson = json.dumps(self.cache, indent=4)
                f.write(cachejson)
        except PermissionError:
            self.log.debug('cannot save cache {}'.format(self.cachepath))
            print(self.cache)
    

    def keypath(self,path):

        if not self.url.endswith('/'):
            self.url+='/'
    
        url = self.url+'getkeyval/{}/{}'.format(self.textid,path)

        auth=None
        if self.keyuser and self.keypath:
            auth=(self.keyuser,self.keypass)
        
        r = requests.get(url, auth=auth)
        if r.status_code==200:
            self.log.info('got keys OK')
        elif r.status_code == 401:
            self.log.error('Authentication required for getting keypath \'{}\' on project textid \'{}\', user keyuser/keypass'.format(path,self.textid))
            return None
        else:
            self.log.info('okerr getkeyval error {} \'{:.50}\' textid:{} {}'.\
                format(r.status_code,r.text,self.textid,path))
            return None
        
        data = json.loads(r.text)
        return data
        
        

    def update(self,name,status,details=None,
        method=None,tags=None,error=None):
        
        if not self.textid:
            self.log.error('Do not update: no textid')
            return
        
        # fix name
        if name.startswith(':') and self.prefix is not None:
            name = self.prefix+name

        r = None
        
        if not self.url:
            self.log.error("cannot update, url not given!")
            return
        
        
        if not self.url.endswith('/'):
            self.url+='/'
    
        url = self.url+'update'
        
        self.log.debug("update: {}:{} = {} ({}) url: {}".format(self.textid,name,status,details, self.url))

        
        payload={'textid': self.textid, 'name':name, 'status': str(status), 
            'details': details, 'secret': self.secret, 'method': method, 'tags': ','.join(tags),'error': error}

        if self.secret:
            secretlog="[secret]"
        else:
            secretlog="[nosecret]"
        start = time.time()
        
        
        try:
            r = requests.post(url, data=payload)
            if r.status_code==200:
                self.log.info('okerr send update OK textid:{}, {}={} {}'.\
                    format(self.textid,name,status,secretlog))
            else:
                self.log.info('okerr update error {} \'{:.50}\' textid:{}, {}={} {}'.\
                    format(r.status_code,r.text,self.textid,name,status,secretlog))
        
            self.log.debug("Request to URL {}:".format(r.request.url))
            self.log.debug(r.request.body)
            
        except requests.exceptions.ConnectionError as e:
            self.log.info('okerr exception {} textid:{}, {}={} {}'.\
                format(str(e),self.textid,name,status,secretlog))
     
        if r:
            self.log.debug(r.content)
        else:
            self.log.debug("no reply, check log")
        self.log.debug("took {} sec.".format(time.time() - start))


def pid2name(pid):
    for proc in psutil.process_iter():
        if proc.pid==pid:
            return proc.name()
    return ""

def getportstr(expr):
    ports=[]
    cc=[]
  
    if expr is None or expr=='':
        expr='True'

    AF_INET6 = getattr(socket, 'AF_INET6', object())

    proto_map = {
        (AF_INET, SOCK_STREAM): 'tcp',
        (AF_INET6, SOCK_STREAM): 'tcp6',
        (AF_INET, SOCK_DGRAM): 'udp',
        (AF_INET6, SOCK_DGRAM): 'udp6',
    }       
                    
    cc=[]

    for proc in psutil.process_iter():
        try:
            for c in proc.connections():
                if c.status=='LISTEN' or c.status=='NONE':
                    proto=proto_map[(c.family,c.type)]
                    crec = {}
                    crec['proto']=proto
                    crec['ip']=c.laddr[0]
                    crec['port']=c.laddr[1]
                    crec['name']=os.path.basename(proc.exe())

                    if not crec in cc:
                        cc.append(crec)
        except psutil.NoSuchProcess:
            pass

    node = evalidate.evalidate(expr)
    code = compile(node,'<usercode>','eval')
        
    for c in cc:
        if eval(code,{},c):
            clist=[c['name'],c['proto'],c['ip'],str(c['port'])]
            cstr=':'.join(clist)
            ports.append(cstr)
        else:
            pass

    return "\n".join(sorted(ports))


def getiarg(textid,name,iarg,secret,urlprefix='http://update.okerr.com/okerr/'):
    payload={'textid': textid, 'name':name,  
        'secret': secret, 'argname': iarg}

    
    url = urlprefix+'getpub'

    try:
        r = requests.post(url, data=payload)
        if r.status_code==200:
            if not 'urlcontent' in cache:
                cache['urlcontent']={}
            cache['urlcontent'][url]=r.content                
            return r.content
        else:
            log.error('okerr getiarg failed ({}): {}'.\
                format(r.status_code,r.content))
            try:
                cached = cache['urlcontent'][url]
                log.error('use cached value for url {} : {}'.format(url,cached))
                return cached
            except:
                log.error('no cache for url {}'.format(url))
                return ""            
        
    except requests.exceptions.ConnectionError as e:
        log.info('okerr getiarg exception {}'.\
            format(str(e)))
        try:
            cached = cache['urlcontent'][url]
            log.error('use cached value for url {} : {}'.format(url,cached))
            return cached
        except:
            log.error('no cache for url {}'.format(url))
            return ""            
 

