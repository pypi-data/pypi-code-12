# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os

import pkgutil
import os.path
import six


valid_backends = ['PyQt4', 'PyQt5', 'PySide']

def _normalise_name(name):
    for backend in valid_backends:
        if name.lower() == backend.lower():
            return backend
    else:
        raise ValueError('SiQt backend {} is not supported!\n Must be one of {}'.format(
                            name, valid_backends))

def use(backend_name, force=False, mode='strict', matplotlib_hook=False):
    """
    Initialize a SiQt backend.

    Parameters
    ----------
     - backend_name: backend name. One of ['PyQt4', 'PyQt5', 'PySide']
     - force: use import hooks to overwrite direct import of the above
       packages by SiQt
     - mode: the import hooks to use
            * "strict": use the backend as it is
            * "compatible": monkeypatch the backend to smooth the differences bewteen
                        backends (e.g. will add SiQt.QtWidgets with the PyQt4 backend,
                        which was only added in PyQt5)
            * "porting": same as smooth, but prints a warning every time an import hook is used.
     - matplotlib_hook: call matplotlib.use with the correct backend
            when matplotlib is first imported
    """
    import sys
    from .. import this
    #from future.standard_library import RenameImport
    name = _normalise_name(backend_name)
    pkg = pkgutil.find_loader(name)
    if pkg is None:
        raise ImportError('Backend {} does not seem to be installed and cannot be used!')
    if this.backend is not None:
        if this.backend != name:
            print('Warning: SiQt.use should be called before any imports of PyQt/PySide.\n'\
              '         Changing backend on the runtime (i.e. calling it a second time) is not supported!')
        return
    this.backend = name
    if six.PY3:
        path_new = os.path.dirname(pkg.path)
    else:
        path_new = pkg.filename
    this.__path__.append(path_new)

    sys.meta_path.insert(0, RenameImportFinder())
    if six.PY2:
        if this.backend in ['PyQt4', 'PyQt5']:
            import sip # just initializing
    if matplotlib_hook:
        sys.meta_path.insert(0, MatplotlibImporter())


class MatplotlibImporter(object):
    def __init__(self):
        pass

    def find_module(self, fullname, path=None):
        import sys
        if fullname.startswith('matplotlib'):
            sys.meta_path = sys.meta_path[1:] # remove the matplotlib hook
            # now initialize matplotlib with the correct Qt4 backend
            from . import matplotlib
        return None

    def load_module(self, name):
        """This is never going to be called"""
        pass

class RenameImportFinder(object):
    """
    Adapted from http://python-future.org/_modules/future/standard_library.html
    """
    def __init__(self):
        pass

    def find_module(self, fullname, path=None):
        # Handles hierarchical importing: package.module.module2
        for name in valid_backends:
            if fullname.startswith(name):
                print('Finding', fullname, path)
                return RenameImportLoader(fullname, path)
        return None

class RenameImportLoader(object):
    """
    Adapted from http://python-future.org/_modules/future/standard_library.html
    """

    def __init__(self, name, path=None):
        '''
        Pass in a dictionary-like object mapping from old names to new
        names. E.g. {'ConfigParser': 'configparser', 'cPickle': 'pickle'}
        '''
        self.name_orig = name
        self.path = path

    def load_module(self, name, path=None):
        if path is None:
            path = self.path
        #print('Loading', name, path)
        for backend_name in valid_backends:
            if backend_name in name:
                name = name.replace(backend_name, 'SiQt')
                self.name_new = name
                break
        #print('2. Loading', name)
        if name in sys.modules:
            #print('zzzz', name)
            #print(sys.modules.keys())
            module = sys.modules[name]
            if self.name_orig not in sys.modules:
                sys.modules[self.name_orig] = module
        else:
            #print('aaa')
            module = self._find_and_load_module(name, path)
            sys.modules[name] = module
            sys.modules[self.name_orig] = module
        #module.__spec__.name = self.name_orig
        #print(module.__spec__)
        return module


    def _find_and_load_module(self, name, path=None):
        """
        Finds and loads it. But if there's a . in the name, handles it
        properly.
        """
        print('3.', name, path)
        import imp
        bits = name.split('.')
        while len(bits) > 1:
            # Treat the first bit as a package
            packagename = bits.pop(0)
            #print(packagename)
            package = self._find_and_load_module(packagename, path)
            try:
                path = package.__path__
            except AttributeError:
                # This could be e.g. moves.
                #flog.debug('Package {0} has no __path__.'.format(package))
                if name in sys.modules:
                    return sys.modules[name]
                #flog.debug('What to do here?')

        #if six.PY2:
        name = bits[0]
        if name in sys.modules:
            #print('zzzz', name, six.PY2)
            #sys.modules[self.name_orig] = name
            module = sys.modules[name]
            #print(module.__spec__)
        else:
            #print('4.', name, path)
            fp, pathname, description = imp.find_module(name, path)
            print(name, self.name_new,  fp, pathname, description)
            try:
                #print(self.name_orig)
                module = imp.load_module(self.name_orig, fp, pathname, description)
            except Exception as e:
                #if six.PY2:
                #    import importlib
                #    module = importlib.import_module(self.name_orig) 
                #else:
                raise e
            finally:
                if fp:
                    fp.close()
        return module
        #else: # PY3
        #    import importlib.machinery
        #    print('Machinery')
        #    module = importlib.machinery.SourceFileLoader(name, path).load_module()
        #    return module




## some earlier attemps should be removed
#import sys
#
#def name(item):
#    " Return an item's name. "
#    return item.__name__
#    
#def format_arg_value(arg_val):
#    """ Return a string representing a (name, value) pair.
#    
#    >>> format_arg_value(('x', (1, 2, 3)))
#    'x=(1, 2, 3)'
#    """
#    arg, val = arg_val
#    return "%s=%r" % (arg, val)
#
#
#def echo(fn):
#    """ Echo calls to a function.
#    
#    Returns a decorated version of the input function which "echoes" calls
#    made to it by writing out the function's name and the arguments it was
#    called with.
#    """
#    import functools
#    # Unpack function's arg count, arg names, arg defaults
#    @functools.wraps(fn)
#    def wrapped(*v):
#        # Collect function arguments by chaining together positional,
#        # defaulted, extra positional and keyword arguments.
#        v = list(v)
#        name = v[0]
#        if name in valid_backends:
#            v[0] = 'SiQt'
#        elif name == 'SiQt':
#            pass
#        elif hasattr(name, '__spec__'):
#            print(dir(name))
#            spec = name.__spec__
#            spec.name = 'SiQt'
#            name.__name__ = 'SiQt'
#        else:
#            print(name)
#
#        print("%s %s" % (fn, v))
#        res = fn(*v)
#        print("Out: %s" % res)
#        return res
#    return wrapped
#
#
#class HijackPyQtImport(object):
#
#    def find_module(self, fullname, path=None):
#        import sys
#        from .. import this
#        for backend_name in valid_backends:
#            if fullname.startswith(backend_name):
#                fullname_out = fullname.replace(backend_name, 'SiQt')
#                print(backend_name, fullname,  path, fullname_out)
#                print(sys.meta_path)
#                if six.PY3:
#                    import importlib.machinery
#                    print(fullname_out, path)
#                    loader =  importlib.machinery.SourceFileLoader(fullname_out, path)
#                    for attr in dir(loader):
#                        if not attr.startswith('__'):
#                            setattr(loader, attr, echo(getattr(loader, attr)))
#                    return loader
#                    #return self._py3_loader(fullname_out, path)
#                else:
#                    raise NotImplementedError
#        else:
#            return None
