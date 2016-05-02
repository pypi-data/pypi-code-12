# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import model
import app.resources as rc
from tran import TransactionStack


class Friendship(model.TComponent):
    """Implements friendship representation"""
    def __init__(self, **kwargs):
        """ Initialice the friendship. Required parameters:
            target: the friend class
            parent: the child class
        """
        assert 'target' in kwargs
        assert 'parent' in kwargs
        self._target = kwargs['target']
        if 'name' not in kwargs:
            kwargs['name'] = self._target._name
        super(Friendship, self).__init__(**kwargs)
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(Friendship, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['target'] = self._target
        kwargs.update(super(Friendship, self).get_kwargs())
        return kwargs

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("friend")

    @property
    def label(self):
        """Get tree label"""
        return "friend " + self._target.reference

    def OnUndoRedoChanged(self):
        """Make changes in the model as result of change"""
        super(Friendship, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

