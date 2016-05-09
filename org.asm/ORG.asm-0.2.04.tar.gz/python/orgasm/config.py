'''
Created on 4 sept. 2014

@author: coissac
'''

from ConfigParser import SafeConfigParser, NoOptionError
import logging
from os import access
from os import R_OK
import sys
import argparse


def getLogger(config):
    
    rootlogger   = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

    stderrHandler = logging.StreamHandler(sys.stderr)
    stderrHandler.setFormatter(logFormatter)

    rootlogger.addHandler(stderrHandler)
    
    if config.log:
        fileHandler = logging.FileHandler("%s.log" % config.outputname)
        fileHandler.setFormatter(logFormatter)
        rootlogger.addHandler(fileHandler)
    
    try:
        loglevel = getattr(logging, config.get('General','loglevel')) 
    except:
        loglevel = logging.INFO
        
    rootlogger.setLevel(loglevel)
    
    return rootlogger

def str2loglevel(level):
    try:
        level = getattr(logging,level)
    except AttributeError:
        level = logging.INFO
        
    return level  

class Config:
    
    def __init__(self,config):
        self._config=config
        self._key = {}
        self._isValued = {}
        
        self._logger=getLogger(self)
        
    def _getvalue(self,key,section,option,vtype=str):
        if not self._isValued.get('key',False):
            try:
                self._key[key]=vtype(self._config.get(section,option))
            except NoOptionError:
                self._key[key]=None
            self._isValued[key]= True
        return self._key[key]
        
    @property
    def logger(self):
        """
        The logger object usable by the assembler
        """
        return self._logger
    
    @property
    def log(self):
        """
        The file name of the log file. If None then logs are not saved in a file
        """
        log = self._getvalue('log','General','log',bool)
        return log
        
    @property
    def loglevel(self):
        """
        The file name of the log file. If None then logs are not saved in a file
        """
        loglevel = self._getvalue('loglevel','General','loglevel',str2loglevel)
        return loglevel
   

    @property
    def output(self):
        output = self._getvalue('output','General','#@#@#@',str)
        if output is None:
            if self.outputname is not None:
                output = open(self.outputname(),'w')
            else:
                output = sys.stdout
            self._isValued['output']= True
            self._key['output']=output
        return output

    @property
    def seedname(self):
        seedname = self._getvalue('seedname','Probes','seeds',str)
        return seedname
        
    @property
    def indexname(self):
        indexname = self._getvalue('indexname','Data','index',str)
        return indexname
    
    @property
    def outputname(self):
        outputname = self._getvalue('outputname','Data','output',str)
        return outputname
    
    @property
    def seedmincov(self):
        mincov = self._getvalue('mincov','Probes','mincov',int)
        return mincov if mincov > 0 else 1
    
    @property
    def minread(self):
        """
        The minimum count of usable reads to consider an extension
        """
        
        minread = self._getvalue('minread','Extension','minread',int)
        return minread if minread > 0 else None
    
    @property
    def coverage(self):
        """
        The expected sequencing coverage
        """
        
        coverage = self._getvalue('coverage','Extension','coverage',int)
        return coverage if coverage > 0 else None
    
    @property
    def mincov(self):
        """
        The minimum count of observation of a read to consider it during an extension
        """
        mincov = self._getvalue('mincov','Extension','mincov',int)
        return mincov if mincov > 0 else 1
    
    @property
    def minoverlap(self):
        minoverlap = self._getvalue('minoverlap','Extension','minoverlap',int)
        return minoverlap if minoverlap > 0 else 1
    
    @property
    def minratio(self):
        minratio = self._getvalue('minratio','Extension','minratio',float)
        return minratio
    
    @property
    def lowcomplexity(self):
        lowcomplexity = self._getvalue('minratio','Extension','minratio',bool)
        return lowcomplexity
        
    @property
    def back(self):        
        back = self._getvalue('back','Gap-filling','back',int)
        return back if back > 0 else None
    
    @property
    def snp(self):
        snp = self._getvalue('snp','Cleaning','snp',bool)
        return snp
    
    @property
    def smallbranches(self):
        """
        The minimum count of usable reads to consider an extension
        """
        smallbranches = self._getvalue('smallbranches','Cleaning','smallbranches',int)
        return smallbranches if smallbranches > 0 else None
    

    

def getConfigFile(options=None):
    
    configFile = None
    if options is not None:
        if hasattr(options, 'config'):
            if access(options.config,R_OK):
                configFile = options.config
            else:
                raise IOError("Config file : %s not readable" % options.config)
    
    if configFile is not None:
        if access("orgasm.conf",R_OK):
            configFile = "orgasm.conf"
        elif access("~/.orgasm.conf",R_OK):
            configFile = "~/.orgasm.conf"
            
    return configFile

def defaultConfiguration(options=None):
    
    config = SafeConfigParser()
    config.optionxform=str

    config.add_section('General')
    config.set('General', 'log', 'False')
    config.set('General', 'loglevel', 'INFO')
    
    config.add_section('Data')
    
    config.add_section('Probes')
    config.set('Probes', 'seeds',  'protChloroArabidopsis')
    config.set('Probes', 'mincov', '1')
   
    config.add_section('Extension')
    config.set('Extension', 'minread',       '-1')
    config.set('Extension', 'coverage',      '-1')
    config.set('Extension', 'mincov',        '1')
    config.set('Extension', 'minratio',      '0.1')
    config.set('Extension', 'minoverlap',    '50')
    config.set('Extension', 'lowcomplexity', 'False')

    config.add_section('Cleaning')
    config.set('Cleaning', 'smallbranches', '-1')
    config.set('Cleaning', 'snp',           'True')

    config.add_section('Gap-filling')
    config.set('Gap-filling', 'back', '-1')
   
    
    return config

def getConfiguration(options=None):
    
    
    dconfig = defaultConfiguration()
    configFile = getConfigFile(options)
    
    if configFile is not None:
        dconfig.read(configFile)
        
    if options is not None:
        if hasattr(options,'minread') and options.minread is not None:
            dconfig.set('Extension', 'minread', str(options.minread))
    
        if hasattr(options,'coverage') and options.coverage is not None:
            dconfig.set('Extension', 'coverage', str(options.coverage))
    
        if hasattr(options,'minratio') and options.minratio is not None:
            dconfig.set('Extension', 'minratio', str(options.minratio))
    
        if hasattr(options,'mincov') and options.mincov is not None:
            dconfig.set('Extension', 'mincov', str(options.mincov))

        if hasattr(options,'minoverlap') and options.minoverlap is not None:
            dconfig.set('Extension', 'minoverlap', str(options.minoverlap))

        if hasattr(options,'smallbranches') and options.smallbranches is not None:
            dconfig.set('Cleaning', 'smallbranches', str(options.smallbranches))

        if hasattr(options,'outputFilename') and options.outputFilename is None:
            options.outputFilename = options.indexFilename
        
        dconfig.set('Data', 'index', options.indexFilename)
        dconfig.set('Data', 'output', options.outputFilename)
            
        if options.log:
            dconfig.set('General', 'log', True)
        
        if options.back is not None:
            dconfig.set('Gap-filling', 'back', str(options.back))
    
        if options.seeds is not None:
            dconfig.set('Probes', 'seeds', str(options.seeds))
   
        
        
    return Config(dconfig)
