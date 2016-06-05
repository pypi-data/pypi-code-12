# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
import model
import app.resources as rc


#def name(x):
#    """comparison"""
#    return x._name


class TypesFolder(model.Folder):
    """Implements a Folder representation"""
    class_container = False
    type_container = True
    function_container = False
    variable_container = False
    module_container = False
    namespace_container = False
    function_container = False
    member_container = False

    #visual methods
    def draggable(self):
        """returns info about if the object can be moved"""
        return False

    def __init__(self, **kwargs):
        """Initialization"""
        from Type import Type
        kwargs['name'] = 'Types'
        super(TypesFolder, self).__init__(**kwargs)
        #create basic read-only types
        for x in ['bool', 'char', 'char16_t', 'char32_t', 'double', 'float',
            'int', 'long', 'long long', 'long double', 'short',
            'unsigned char', 'unsigned int', 'unsigned long', 'unsigned long long',
            'unsigned short', 'void']:
            Type(parent=self, name=x, readonly=True)
        #add unnamed type for functions with implicit type
        Type(parent=self, name='', readonly=True, visibleInTree=False)
        #add @ type for on-the-fly template types
        Type(parent=self, name='@', readonly=True, visibleInTree=False)
        self[Type].sort(key=lambda x: x._name, reverse=False)
        self.update_container()

    def update_container(self):
        """Update the container info"""
        self.context_container = False
        self.folder_container = False
        self.diagram_container = False
        self.namespace_container = False

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folderT")

    def ExistMemberDataNamed(self, name):
        """Check recursively about the existence of nested child member"""
        return False


