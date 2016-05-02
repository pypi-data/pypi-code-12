# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

import model
import tran
import app.resources as rc


class Import(model.TComponent):
    """Implements argument representation"""

    context_container = False

    #visual methods
    @tran.TransactionalMethod('move import {}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_import_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0  # trick for insert as first child
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        self._as = kwargs.get('as', None)
        self._from = kwargs.get('from', None)  # (list of modules)
        super(Import, self).__init__(**kwargs)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Import, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['as'] = self._as
        kwargs['from'] = self._from
        kwargs.update(super(Import, self).get_kwargs())
        return kwargs

    def OnUndoRedoChanged(self):
        """Update from app"""
        self.parent.OnUndoRedoChanged()
        super(Import, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self, root=True):
        """Do required actions for removing"""
        super(Import, self).OnUndoRedoRemoving(root)
        self.parent.OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        self.parent.OnUndoRedoChanged()
        super(Import, self).OnUndoRedoAdd()

    def ExportPythonCode(self, wf):
        """Write code"""
        wf.writeln(self.label)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('py_import')

    @property
    def label(self):
        """Get tree label"""
        if self._from:
            if self._as:
                return 'from {self._name} import {self._from} as {self._as}'.format(self=self)
            else:
                return 'from {self._name} import {self._from}'.format(self=self)
        if self._as:
            return 'import {self._name} as {self._as}'.format(self=self)
        return 'import {self._name}'.format(self=self)
