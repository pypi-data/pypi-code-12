#!/usr/bin/env python
import copy
import inspect
import os
import sys

def caller_modules():
    try:
        frames = inspect.getouterframes(inspect.currentframe())
        modules = []
        # frame,filename,line_number,function_name,lines,index
        for frame,_,_,_,_,_ in frames:
            module = inspect.getmodule(frame)
            if module and module not in modules:
                modules.append(module)
        return modules
    except IndexError:
        return []

def append(module,name):
    __all__ = module.__dict__.setdefault('__all__', [])
    if name not in __all__:  # Prevent duplicates if run from an IDE.
        __all__.append(name)
        #if debug:
            #print("%s.__all__ +%s" % (module.__name__,name))
        setattr(module,"__all__",sorted(__all__))

def isstring(object):
    try:
        int(object)
        return False
    except ValueError:
        return True
    except Exception:
        return False

def equal_id(object1,object2):
    return id(object1)==id(object2)

def validate_module(module):
    if module is None:
        err = "module is None"
        raise Exception(err)
    if not hasattr(module,"__file__"):
        # system module?
        err = "%s has no attribute __file__" % module
        raise Exception(err)


def publish2module(object,module,force=False):
    validate_module(module)
    file = module.__file__
    if isstring(object): # text
        name = object
        dirname = os.path.dirname(file)
        if not hasattr(module,name) and not force:
            # not object name or not exists
            # object str value?
            for mname,member in inspect.getmembers(module):
                if equal_id(member,name):
                    return publish2module(mname,module)
        append(module,name)
        ismod = os.path.basename(file).find("__init__")!=0
        if ismod:
            # find parent package
            # iterate sys.modules
            for _,m in copy.copy(sys.modules).items():
                if not m or not hasattr(m,"__file__"):
                    continue
                ispkg = os.path.basename(m.__file__).find("__init__.py")==0
                if ispkg and os.path.dirname(m.__file__)==dirname:
                    publish2module(name,m)
        return
    if inspect.isclass(object) or inspect.isroutine(object): 
        name = object.__name__
        return publish2module(name,module,force=True)
    # find object, compare by id
    for mname,member in getmembers(module):
        if equal_id(member,object):
            return publish2module(mname,module)
    # fix imp.load_module with custom name
    # search same module
    for _,m in modules.items():
        if m and hasattr(m,"__file__") and m.__file__==file:
            module = m
            for mname,member in getmembers(module):
                if equal_id(member,object):
                    return publish2module(mname,module)
            for mname,member in getmembers(module):
                if member==object:
                    return publish2module(mname,module)
    # find object last try
    for mname,member in getmembers(module):
        if member==object:
            return publish2module(mname,module)
    err = "%s not exists in %s" % (object,module)
    raise Exception(err)

def public(*objects):
    """public decorator for __all__
    """
    modules = caller_modules()
    if len(modules)==1 or (objects and objects[0]==public):
        module = modules[0]
    else:
        modules = modules[1:] # exclude public
        module = modules[0]
    if not module: # error?
        if len(objects)==1:
            return objects[0]
        else:
            return objects
    for _object in objects:
        if not hasattr(_object,"__name__"):
            for k,v in module.__dict__.items():
                if v==_object:
                    _object=k
        if not (inspect.isclass(_object) or inspect.isfunction(_object) or isstring(_object)):
            err = "@public expected class, function or str object name"
            raise TypeError(err)
        modname = module.__name__
        modnames = modname.split(".")
        for i,modname in enumerate(modnames):
            fullname = ".".join(modnames[0:i+1])
            if fullname in sys.modules:
                module = sys.modules[fullname]
                publish2module(_object,module)
    if len(objects)==1:
        return objects[0]
    else:
        return objects

public(public)

if __name__=="__main__":
    print(__all__)
    
    # @public
    @public
    def func(): pass
    print(__all__)

    # public(*objects)
    def func2(): pass
    public(func2)
    print(__all__)
    public("func3")
    print(__all__)

    kwargs=dict(k="v")
    public(kwargs)
    print(__all__)

