# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

import model
import tran
import app.resources as rc
from tran import TransactionStack


class Argument(model.TComponent):
    """Implements argument representation"""

    context_container = True

    #visual methods
    @tran.TransactionalMethod('move argument {}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_argument_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0  # trick for insert as first child
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        self._typei = kwargs['type']
        self._default = kwargs.get('default', '')
        super(Argument, self).__init__(**kwargs)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(Argument, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['type'] = self._typei
        kwargs['default'] = self._default
        kwargs.update(super(Argument, self).get_kwargs())
        return kwargs

    def OnUndoRedoChanged(self):
        """Update from app"""
        self.parent.OnUndoRedoChanged()
        super(Argument, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoRemoving(self, root=True):
        """Do required actions for removing"""
        super(Argument, self).OnUndoRedoRemoving(root)
        self.parent.OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        self.parent.OnUndoRedoChanged()
        super(Argument, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('member')

    @property
    def tree_label(self):
        """Get tree label"""
        init = ''
        if len(self._default) > 0:
            init += "=" + self._default
        return (str(self._typei).format(self._name) + init).encode('ascii', 'ignore')

    @property
    def implement(self):
        """return the label whitout default value"""
        return str(self._typei).format(self._name).encode('ascii', 'ignore')

    @property
    def declare(self):
        """return the label whitout default value"""
        init = ''
        if len(self._default) > 0:
            init += "=" + self._default
        return (str(self._typei).format(self._name) + init).encode('ascii', 'ignore')

