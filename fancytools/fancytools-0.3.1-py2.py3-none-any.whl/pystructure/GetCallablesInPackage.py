import importlib
import inspect

from fancytools.fcollections.NestedOrderedDict import NestedOrderedDict


class GetCallablesInPackage(NestedOrderedDict):
    '''
    Return a NestedOrderedDict of all functions and classes within a given package.
    excluding 'private' modules beginning with '_'

    =========  ======================================
    Arguments  Description
    =========  ======================================
    package    package or string of path to package
               to get all callables from
    =========  ======================================


    =====================  =======  ===============================
    Optional               Default  Description
    =====================  =======  ===============================
    modules_in_structure   False    include the modules of the 
                                    callables in the output
    include_classes        True     include classes in the output
    include_functions      True     include functions in the output
    min_level              0        minimum depth level in the 
                                    package structure
    max_level              None     maximum depth level in the 
                                    package structure
    exclude_empty_pck      True     exclude sub-packages without 
                                    any callables from the output
    =====================  =======  ===============================


    '''
    def __init__(self, package, modules_in_structure=False, 
                 include_classes=True, include_functions=False, 
                 min_level=0, max_level=None, exclude_empty_pck=True):
        '''
        '''

        NestedOrderedDict.__init__(self)

        if isinstance(package, basestring):
            package = importlib.import_module(package)
            
        self._package = package
        self._include_classes = include_classes
        self._include_functions = include_functions           
        self._modules_in_structure = modules_in_structure
        self._min_level = min_level
        self._max_level = max_level
        
        self._objects = [package]
        
        self._buildRecursive(package, self, 0)
        
        if exclude_empty_pck:
            self._cleanRecursive(self)
      
            
    def _cleanRecursive(self, subSelf):
        '''
        Delete all NestedOrderedDict that haven't any entries.
        '''
        for key, item in subSelf.iteritems():
            if self.isNestedDict(item):
                if not item:
                    subSelf.pop(key)
                else:
                    self._cleanRecursive(item)
            
    
    
    def _buildRecursive(self, module, subSelf, level):

        for (name, obj) in inspect.getmembers(module):
            # take only 'public' modules
            if name[0] == '_':
                continue
            #print name, level
            if inspect.ismodule(obj):
                #don't handle modules thats have been used before:
                if obj in self._objects:
                    continue
                self._objects.append(obj)

                if obj.__name__.startswith(self._package.__name__):
                    #either use module for submenus or check whether module is actually a package:
                    if self._modules_in_structure or obj.__file__.endswith('__init__.pyc'):
                        #limit max recursion level
                        if not self._max_level or level <= self._max_level:
                        #if self._max_level:
                            l = subSelf[name] = NestedOrderedDict()
                            self._buildRecursive(obj, l, level+1)
                    else:
                        #use same menu for all classes of all files on one folder/module
                        self._buildRecursive(obj, subSelf, level)
                    
            elif level >= self._min_level: 
                    # if object is a class 
                    if ( 
                        ( self._include_classes and inspect.isclass(obj) ) or #( not self._include_classes or ( self._include_classes and inspect.isclass(obj) ) or 
                    # and/or a function 
                       ( self._include_functions and inspect.isfunction(obj) ) #( not self._include_functions or ( self._include_functions and inspect.isfunction(obj)) )
                        ):
                        # if object belongs to its parent module (mod is not imported)
                        # OR module paths are the same (in case of from mod import cls and cls.name == mod.name)
                        try:
                            if self.belongsToModule(obj, module):
                                subSelf[name] = obj
                        except AttributeError:
                            pass # obj has no __module__ is e.g. a string


    @staticmethod
    def belongsToModule(obj, module):
        '''Returns True is an object belongs to a module.'''
        return obj.__module__ == module.__name__ or obj.__module__.startswith(module.__name__)
    

    def buildHirarchy(self, horizontal_operation=None, vertical_operation=None):
        '''Walk through the nested dict structure and executes 
        horizontal_operation(name, callable) resp. 
        vertical_operation(name, callable) if defined.
        '''
        def buildRecursive(pkey, pval):
            if self.isNestedDict(pval):
                if vertical_operation:
                    vertical_operation(pkey, pval) 
                for key, val in pval.iteritems():
                    #if not isinstance(val, NestedOrderedDict):
                    buildRecursive(key, val)
            else:
                if horizontal_operation:
                    horizontal_operation(pkey, pval) 
        buildRecursive(self._package.__name__, self)       


    @staticmethod
    def isNestedDict(instance):
        '''convenience function for 
        
        >>> isinstance(instance, NestedOrderedDict)'''
        return isinstance(instance, NestedOrderedDict)





if __name__ == '__main__':
    import sys
    import numpy
    g = GetCallablesInPackage(numpy, include_functions=True)
    print g

    
    class printClassStructure(object):
        def __init__(self): 
            self.indent = ''
            self._hor_as_last_called = True

        def hor(self, key, item):
            sys.stdout.write("%s%s - " %(self.indent,key) )
            self.indent = ''
            self._hor_as_last_called = True

        def vert(self, key, item):
            if self._hor_as_last_called:
                print ''
            print "%s-> %s" %(self.indent,key)
            self.indent += '\t'
            self._hor_as_last_called = False
            
    p = printClassStructure()
    
    g.buildHirarchy(horizontal_operation=p.hor, 
                    vertical_operation=p.vert)
