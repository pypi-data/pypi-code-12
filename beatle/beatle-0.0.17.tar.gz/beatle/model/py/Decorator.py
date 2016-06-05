# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

import model
import tran
import app.resources as rc


class Decorator(model.TComponent):
    """Implements Decorator representation"""
    argument_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        self._call = kwargs.get("call", False)
        super(Decorator, self).__init__(**kwargs)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None
        parent = self.parent
        if type(parent) is model.py.MemberMethod:
            if self.name == 'staticmethod':
                parent._staticmethod = self
            elif self._name == 'classmethod':
                parent._classmethod = self
            elif self._name == 'property':
                parent._property = self
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Decorator, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Decorator, self).get_kwargs()

    def OnUndoRedoChanged(self):
        """Update from app"""
        self.parent.OnUndoRedoChanged()
        super(Decorator, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self):
        """Do required actions for removing"""
        parent = self.parent
        if type(parent) is model.py.MemberMethod:
            if parent._staticmethod == self:
                parent._staticmethod = None
            elif parent._classmethod == self:
                parent._classmethod = None
            elif parent._property == self:
                parent._property = None
        super(Decorator, self).OnUndoRedoRemoving()
        self.parent.OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        self.parent.OnUndoRedoChanged()
        super(Decorator, self).OnUndoRedoAdd()
        parent = self.parent
        if type(parent) is model.py.MemberMethod:
            if self.name == 'staticmethod':
                parent._staticmethod = self
            elif self._name == 'classmethod':
                parent._classmethod = self
            elif self._name == 'property':
                parent._property = self

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('decorator')

    def ExportPythonCode(self, wf):
        """Export python code"""
        wf.writeln(self.label)

    @property
    def label(self):
        """Get tree label"""
        if self._call:
            from Argument import Argument
            from ArgsArgument import ArgsArgument
            from KwArgsArgument import KwArgsArgument
            alist = ', '.join(arg.label for arg in
                self[Argument] + self[ArgsArgument] + self[KwArgsArgument])
            return '@{self._name}({alist})'.format(self=self, alist=alist)
        else:
            return '@{self._name}'.format(self=self)




