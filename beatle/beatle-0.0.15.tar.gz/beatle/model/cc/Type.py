# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import model
import app.resources as rc
from tran import TransactionStack


class Type(model.TComponent):
    """Implements class representation"""
    def __init__(self, **kwargs):
        """Initialization method"""
        self._access = kwargs.get('access', "public")
        self._definition = kwargs.get('definition', "")
        self._template = kwargs.get('template', None)
        super(Type, self).__init__(**kwargs)
        self.project.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        project = self.project
        super(Type, self).Delete()
        project.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['access'] = self._access
        kwargs['definition'] = self._definition
        kwargs['template'] = self._template
        kwargs.update(super(Type, self).get_kwargs())
        return kwargs

    @property
    def template_args(self):
        """Retorna una cadena que representa los argumentos del patron.
        Por ejemplo, si la cadena del template es 'typename T,class S=x'
        retorna T,S. Por el momento no se considera el uso de variadic"""
        if self._template is None:
            return ''
        s = str(self.template_types)[1:-1]
        s = s.replace("u'", '')
        s = s.replace('u"', '')
        s = s.replace("'", '')
        s = s.replace('"', '')
        return s

    @property
    def template_types(self):
        """Retorna la lista de identificadores de tipo utilizados
        en la declaracion de patron"""
        if self._template is None:
            return []
        l = self._template.split(',')
        prologs = ['int', 'class', 'typename']
        r = []
        for u in l:
            v = u.split('=')[0]
            for p in prologs:
                v = v.replace(p, '')
            r.append(v.strip())
        return r

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(Type, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(Type, self).RestoreRelations()

    def OnUndoRedoRemoving(self, root=True):
        """Prepare object to delete"""
        super(Type, self).OnUndoRedoRemoving(root)

    @property
    def can_delete(self):
        """Comprueba si el tipo puede ser eliminado"""
        if self._readOnly:
            return False
        project = self.project
        #Obtenemos la lista de miembros de clase
        if not project is None:
            #comprobamos si el tipo esta siendo utilizado
            typed = project(model.cc.MemberData, model.cc.MemberMethod, model.cc.Argument)
            for x in typed:
                if x._typei._type == self:
                    return False
            return True

    def OnUndoRedoChanged(self):
        """Update from app"""
        #Obtenemos la lista de miembros de clase
        super(Type, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Type, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("type", self._access)

    @property
    def scoped(self):
        """Get the scope"""
        return '{self.parent.scope}{self._name}'.format(self=self)

    def scoped_str(self, scope_list):
        """Gets the string representation with minimal relative scope"""
        s = self.scoped
        best_match = 0
        best_scope = None
        for x in scope_list:
            if s.find(x) == 0:
                if len(x) > best_match:
                    best_match = len(x)
                    best_scope = x
        if best_scope:
            s = s[best_match:]
            if s[:2] == '::':
                s = s[2:]
        return s

    @property
    def tree_label(self):
        """Get tree label"""
        # modify old versions
        if not hasattr(self, '_template'):
            self._template = None
        #endif
        if self._template is not None:
            return '{self._name}<{self.template_args}>'.format(self=self)
        return self._name


class typeinst(object):
    """This class represents the common usage of a type"""
    def __init__(self, **kwargs):
        """Initialice type instance"""
        self._type = kwargs.get('type', None)
        self._const = kwargs.get('const', False)
        self._ptr = kwargs.get('ptr', False)
        self._ref = kwargs.get('ref', False)
        self._ptr_to_ptr = kwargs.get('ptrptr', False)
        self._const_ptr = kwargs.get('constptr', False)
        self._array = kwargs.get('array', False)
        self._array_size = kwargs.get('arraysize', 0)
        self._funptr = kwargs.get('funptr', False)
        self._type_alias = kwargs.get('type_alias', None)   # for on-the-fly template types
        self._type_args = kwargs.get('type_args', None)   # for template types instance
        if self._funptr:
            self._argdecl = kwargs.get('argdecl', '()')
        super(typeinst, self).__init__()

    @property
    def type_name(self):
        """Return effective type name"""
        if self._type_alias is not None:
            return self._type_alias
        else:
            return self._type._name

    @property
    def is_ptr(self):
        """Return info about if the type is a pointer"""
        return self._ptr

    @property
    def base_type(self):
        """Return the base type"""
        return self._type

    @property
    def scoped(self):
        """Get the scope"""
        if self._type_alias is not None:
            return self._type_alias
        else:
            return self._type.scoped

    def scoped_str(self, scope_list):
        """Gets the string representation with minimal relative scope"""
        s = self.scoped
        best_match = 0
        best_scope = None
        for x in scope_list:
            if s.find(x) == 0:
                if len(x) > best_match:
                    best_match = len(x)
                    best_scope = x
        if best_scope:
            s = s[best_match:]
            if s[:2] == '::':
                s = s[2:]
        if self._type_args is not None:
            s = s + '<{}>'.format(self._type_args)
        if self._const:
            s = "const " + s
        if self._ptr:
            s += "*"
        if self._const_ptr:
            s += " const"
        if self._ptr_to_ptr:
            s += "*"
        if self._ref:
            s += "&"
        if self._funptr:
            s += ' (*{})' + self._argdecl
        else:
            s += ' {}'
        if self._array:
            if type(self._array_size) is str:
                s += '[{}]'.format(self._array_size)
            else:
                s += '[{}]'.format(str(self._array_size))
        return s

    def __str__(self):
        """Returns the type string format"""
        # migrate old versions
        if not hasattr(self, '_type_args'):
            self._type_args = None
        #end
        if self._type_alias is not None:
            s = self._type_alias    # used for on-the-fly template types
        else:
            s = self._type._name
        if self._type_args is not None:
            s = s + '<{}>'.format(self._type_args)
        if self._const:
            s = "const " + s
        if self._ptr:
            s += "*"
        if self._const_ptr:
            s += " const"
        if self._ptr_to_ptr:
            s += "*"
        if self._ref:
            s += "&"
        if self._funptr:
            s += ' (*{})' + self._argdecl
        else:
            s += ' {}'
        if self._array:
            if type(self._array_size) is str:
                s += '[{}]'.format(self._array_size)
            else:
                s += '[{}]'.format(str(self._array_size))
        return s

