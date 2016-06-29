# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
from MemberMethod import MemberMethod


class ExitMethod(MemberMethod):
    """Implements is_class method"""
    context_container = True
    argument_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs['name'] = '__exit__'
        kwargs['readonly'] = True
        super(ExitMethod, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(ExitMethod, self).get_kwargs())
        return kwargs

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(ExitMethod, self).OnUndoRedoChanged()

    #def OnUndoRedoRemoving(self, root=True):
    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        super(ExitMethod, self).OnUndoRedoRemoving()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(ExitMethod, self).OnUndoRedoAdd()
