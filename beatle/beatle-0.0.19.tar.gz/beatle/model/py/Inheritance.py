# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import model
import app.resources as rc
from tran import TransactionStack


class Inheritance(model.TComponent):
    """Implements class representation"""
    def __init__(self, **kwargs):
        """ Initialice the inheritance. Required parameters:
                ancestor: the parent class
            parent: the child class
            Optional parameters are:
               name: the name of the inheritance. This parameter is
            really not expected, because the inheritance cannot be aliased."""
        assert 'ancestor' in kwargs
        assert 'parent' in kwargs
        self._ancestor = kwargs['ancestor']
        if 'name' not in kwargs:
            kwargs['name'] = self._ancestor._name
        super(Inheritance, self).__init__(**kwargs)
        #prevent external inheritances hangs
        if self._ancestor:
            self._ancestor._deriv.append(self.parent)
        if not kwargs.get('raw', False):
            self.parent.AutoInit()
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Inheritance, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['ancestor'] = self._ancestor
        kwargs.update(super(Inheritance, self).get_kwargs())
        return kwargs

    def SetAncestor(self, ancestor):
        """Update ancestor"""
        if self._ancestor != ancestor:
            if not self._ancestor is None:
                self._ancestor._deriv.remove(self.parent)
        self._ancestor = ancestor
        if not self._ancestor is None:
            self._ancestor._deriv.append(self.parent)
            self._name = self._ancestor._name

    def RemoveRelations(self):
        """Utility for undo/redo"""
        if self._ancestor:
            self._ancestor._deriv.remove(self.parent)
        super(Inheritance, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        if self._ancestor:
            self._ancestor._deriv.append(self.parent)
        super(Inheritance, self).RestoreRelations()

    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        if not TransactionStack.InUndoRedo():
            project = self.project
            if project is not None:
                # remove from diagrams
                dias = project(model.ClassDiagram)
                for dia in dias:
                    # Check if inherit is in
                    elem = dia.FindElement(self)
                    if elem is not None:
                        TransactionStack.DoSaveState(dia)
                        dia.RemoveElement(elem)
        super(Inheritance, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Reflect changes"""
        for x in self.parent._deriv:
            x.OnUndoRedoChanged()
        super(Inheritance, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        #self._ancestor._deriv.append(self.parent)
        if not TransactionStack.InUndoRedo():
            # Check class diagrams for update
            project = self.project
            if project is not None:
                dias = project(model.ClassDiagram)
                for dia in dias:
                    # If inheritance is already, skip
                    if dia.FindElement(self) is not None:
                        continue
                    # Check if both classes are represented in
                    parent = dia.FindElement(self._ancestor)
                    if parent is None:
                        continue
                    child = dia.FindElement(self.inner_class)
                    if child is None:
                        continue
                    # Inheritance must be added to transaction
                    # (even when hidden)
                    TransactionStack.DoSaveState(dia)
                    dia.AddInheritance(self, parent, child)
        super(Inheritance, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_inheritance")

    @property
    def tree_label(self):
        """Get tree label"""
        return "inherits " + self._name


