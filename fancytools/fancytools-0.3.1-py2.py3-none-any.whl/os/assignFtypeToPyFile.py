# -*- coding: utf-8 -*-
import os
import sys


from .isAdmin import isAdmin



def assignFtypeToPyFile(extension, args=(), mimetype=None, showTerminal=True):    
    '''
    Connect a file extension to a python script
    
    Example:
    We created a python file that can open '.da' files
    The command we need to execute to open that is is:
    'python MY_PYTH_FILE.py -o MY_DA_FILE.da'
    
    To be able to open these files with a simple double click run:
    
    openExtensionWith(extension='da', args=('MY_PYTH_FILE.py', '-o'))
    
    OPTIONAL ARGUMENTS:
    args -> (...) additional arguments to be added after the pyFile 
    
    mimetype (str) -> assign a MIMETYPE name to your file extension
        e.g. 'daFile'
        
    
    showTerminal (bool) -> True: open your program in a terminal
    '''
    #WINDOWS
    if os.name == 'nt':
        if not isAdmin():
            raise Exception('need to have admin rights to connect a file extension to program')
        
        if getattr(sys, 'frozen', False):
            #in case we run from an executable e.g. created with pyinstaller:
            py_exec = sys.executable
        else:
            py_exec = sys.exec_prefix
            if showTerminal:
                py_exec += '\\python.exe'
            else:
                py_exec += '\\pythonw.exe'
        
        #associate extension witrh MIME type:
        os.system("assoc .%s=%s" %(extension, mimetype))

        if type(args) not in (tuple,list):
            args = (args,)
        if len(args) == 1:
            str_args = ''' "%s"''' %args[0]
        else:
            str_args = ""
            for a in args:
                str_args += ''' "%s"''' %a
        #open MIME type with pyFile:        
        os.system("""ftype %s="%s" %s"""%(mimetype,py_exec,str_args) + """ "%1" %*""")
    #LINUX
    #check the os to setup further procedures
    #elif os.name == 'posix': #for linux-systems
    #    self.__class__ = _LinuxOpenExtensionWith        
    
    #MAC
    else:
        raise OSError('creating start menu entries is not implemented for this OS at the moment')



# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()