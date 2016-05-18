import os
import sys
import imp
import pdb as pdb_module
from  fnmatch import fnmatch

from karmadbg.dbgcore.macro import macrocmd, macroList, MacroError, registerMacro
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.dbgserver import dbgserver

@macrocmd
def help(*args):
    '''
    interactive help
    '''
    return "help meeeeeeeeeeeeeee!"


@macrocmd
def macrolist(*args):
    '''
    print all registered macro commands
    '''
    match = args[0] if len(args) > 0 else "*"

    return "\n".join( filter( lambda x: fnmatch(x, match), sorted(macroList) ) )

@macrocmd
def macrohelp(*args):
    '''
    print description for macro command

    %macrohelp [macroname]
    '''
    if len(args) == 0:
        return macrohelp.__doc__

    macroName = args[0]

    if macroName in macroList:
        fn, desc = macroList[macroName]
        return desc
    else:
        raise MacroError("macro \'%s\' not found" % macroName)


class PdbAutoDbg(object):

    def __enter__(self):
        self.origtrace = sys.gettrace()
        pdb_module.Pdb( skip=['*.stdmacro', 'dbgcore.*'] ).set_trace()
                
    def __exit__(self, type, value, traceback):
        sys.settrace(self.origtrace)

@macrocmd
def pdb(fileName, *args):

    '''
    run script with standard pdb debugger
    '''

    argv = sys.argv
    __name__ = globals()["__name__"]
    __file__ =  globals()["__file__"]

    try:

        dirname, _ = os.path.split(fileName)

        if not dirname:
            script, suffix = os.path.splitext(fileName)
            _,fileName,desc=imp.find_module(script)

        globals()["__name__"] = "__main__"
        globals()["__file__"] = fileName

        sys.argv = []
        sys.argv.append(fileName)
        sys.argv.extend(args)

        
        with PdbAutoDbg() as dbg:
            execfile(fileName)

    except:
        sys.stderr.write(showtraceback( sys.exc_info(), 2 ))
        pass

    sys.argv = argv
    globals()["__name__"] = __name__
    globals()["__file__"] = __file__


@macrocmd
def run(scriptname, *args):

    '''
    run script
    '''

    dbgserver.runCodeCommand(scriptname, args)
    

@macrocmd
def rund(scriptname, *args):
    '''
    run script with debugger
    '''

    dbgserver.runCodeCommand(scriptname, args, debug=True)

@macrocmd(name = 'exec')
def exec_ (codestr):
    '''
    execute statement
    '''
    dbgserver.execCode(codestr)


@macrocmd
def execd(codestr):
    '''
    execute statement with debugger
    '''
    dbgserver.execCode(codestr, debug = True)

@macrocmd
def edit(fileName):

    '''
    run notepad for specified file
    '''
    import os
    cmd = "notepad " + fileName
    print cmd
    os.system(cmd)

@macrocmd
def time(scriptname, *args):

    '''
    run script with time measurement
    '''

    import time

    t1 = time.time()
    dbgserver.runCodeCommand(scriptname, args)
    t2 = time.time()

    print "\nWall time:", "%.3fs" % (t2-t1)

