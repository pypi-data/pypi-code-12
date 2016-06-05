# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
from MemberMethod import MemberMethod


class InitMethod(MemberMethod):
    """Implements is_class method"""
    context_container = True
    argument_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs['name'] = '__init__'
        kwargs['readonly'] = True
        super(InitMethod, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(InitMethod, self).get_kwargs())
        return kwargs

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(InitMethod, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        super(InitMethod, self).OnUndoRedoRemoving()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(InitMethod, self).OnUndoRedoAdd()
