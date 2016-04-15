'''
Created on 24 mai 2015

@author: coissac
'''
from distutils.version import StrictVersion
from distutils import sysconfig
import subprocess
import os
import glob
import re

from obidistutils.serenity.checksystem import is_windows_system
import sys


def is_python_version(path=None,minversion='3.4',maxversion=None):
    '''
    Checks that the python version is in the range {minversion,maxversion[
    
        @param path: if None consider the running python
                     otherwise the python pointed by the path
        @param minversion: the minimum version to consider
        @param maxversion: the maximum version to consider (strictly inferior to)
                     
        @return: True if the python version match
        @rtype: bool
    '''
    if path is None:
        pythonversion = StrictVersion(sysconfig.get_python_version())
    else:
        command = """'%s' -c 'from distutils import sysconfig; """ \
                  """print(sysconfig.get_python_version())'""" % path
                  
        p = subprocess.Popen(command, 
                             shell=True, 
                             stdout=subprocess.PIPE)
        pythonversion=str(p.communicate()[0],'utf8').strip()
        pythonversion = StrictVersion(pythonversion)
                        
    return  (        pythonversion >=StrictVersion(minversion) 
             and (   maxversion is None    
                  or pythonversion < StrictVersion(maxversion))
            )
           

def lookfor_good_python(minversion='3.4',maxversion=None,followLink=False):
    '''
    Look for all python interpreters present in the system path that
    match the version constraints.
    
    @param minversion: the minimum version to consider
    @param maxversion: the maximum version to consider (strictly inferior to)
    @param followLink: a boolean value indicating if link must be substituted 
                       by their real path.
                       
    @return: a list of path to interpreters
    '''
    exe = []
    if not is_windows_system():
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            candidates = glob.glob(os.path.join(p,'python*')) 
            pexe = []
            pythonpat=re.compile('python([0-9]|[0-9]\.[0-9])?$')
            for e in candidates:
                print(e)
                if pythonpat.search(e) is not None:
                    if followLink and os.path.islink(e):
                        e = os.path.realpath(e)
                    if (os.path.isfile(e) and 
                       os.access(e, os.X_OK) and 
                       is_python_version(e,minversion,maxversion)):
                        pexe.append(e)
            exe.extend(set(pexe))
        
    return exe

def is_a_virtualenv_python(path=None):
    '''
    Check if the python is belonging a virtualenv
    
        @param path: the path pointing to the python executable.
                     if path is None then the running python is
                     considered.
        @param path: str or None 
                     
        @return: True if the python belongs a virtualenv
                 False otherwise
        @rtype: bool
                 
    '''
    if path is None:
        rep = sys.base_exec_prefix != sys.exec_prefix
    else:
        command = """'%s' -c 'import sys; print(sys.base_exec_prefix != sys.exec_prefix)'""" % path
        p = subprocess.Popen(command, 
                             shell=True, 
                             stdout=subprocess.PIPE)
        rep = eval(str(p.communicate()[0],'utf8'))
        
    return rep


def which_virtualenv(path=None,full=False):
    '''
    Returns the name of the virtualenv.
        @param path: the path to a python binary or None
                     if you want to consider the running python
        @type path: str or None
                     
        @param full: if set to True, returns the absolute path,
                     otherwise only return a simple directory name
        @type full: bool
                 
        @return: the virtual environment name or None if the
                 path does not belong a virtualenv
        @rtype: str or None
    '''
    if path is None:
        path = sys.executable
    
    if is_a_virtualenv_python(path):
        parts = path.split(os.sep)
        try:
            if full:
                rep = os.sep.join(parts[0:parts.index('bin')])
                rep = os.path.realpath(rep)
            else:
                rep = parts[parts.index('bin')-1]
        except ValueError:
            rep = None
    else:
        rep=None
        
    return rep
        

