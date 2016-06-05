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
        self._access = kwargs.get('access', "public")
        self._virtual = kwargs.get('virtual', False)
        if 'name' not in kwargs:
            scoped = lambda x: (hasattr(x, 'scoped') and x.scoped) or x.name
            kwargs['name'] = scoped(self._ancestor)
        super(Inheritance, self).__init__(**kwargs)
        self._ancestor._deriv.append(self.parent)
        self.parent.AutoInit()
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)


    def Delete(self):
        """Handle delete"""
        diagrams = [(x, x.FindElement(self)) for x in self.project(model.ClassDiagram)]
        for diagram, element in diagrams:
            if element:
                diagram.SaveState()
                diagram.RemoveElement(element)
        k = self.outer_class or self.outer_module
        super(Inheritance, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['ancestor'] = self._ancestor
        kwargs['access'] = self._access
        kwargs['virtual'] = self._virtual
        kwargs.update(super(Inheritance, self).get_kwargs())
        return kwargs

    @property
    def virtual_bases(self):
        """Gets the list of virtual bases through inheritance"""
        r = self._ancestor.virtual_bases
        if self._virtual and self._ancestor not in r:
            r.append(self._ancestor)
        return r

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
        self._ancestor._deriv.remove(self.parent)
        super(Inheritance, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        self._ancestor._deriv.append(self.parent)
        super(Inheritance, self).RestoreRelations()


    def OnUndoRedoChanged(self):
        """Reflect changes"""
        for x in self.parent._deriv:
            x.OnUndoRedoChanged()
        super(Inheritance, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoRemoving(self):
        super(Inheritance, self).OnUndoRedoRemoving()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        #self._ancestor._deriv.append(self.parent)
        if not TransactionStack.InUndoRedo():
            # Check class diagrams for update
            if project is not None:
                dias = self.project(model.ClassDiagram)
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
        return rc.GetBitmapIndex("inheritance", self._access)

    @property
    def tree_label(self):
        """Get tree label"""
        return "inherits " + self._name


