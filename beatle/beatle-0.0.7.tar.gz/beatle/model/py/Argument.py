# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

import model
import tran
import app.resources as rc


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
        # arguments:
        # ... default : the default or the call value
        # ... context : the use case. may be:
        #    ... declare : when the argument represents a argument declaration
        #    ....value : when the argument represents a value in call (the name is irrelevant)
        #    ....keyword : when the argument represent a keyword value in call (default is mandatory)
        #    ....starargs : when the argument represent a star args in call
        #    ....kwargs : when the argument represent a keyword args in call
        #
        # normal context is declare. The rest of contexts are argument-reuse for few cases, like
        # decorator instantiations
        self._default = kwargs.get('default', '')
        self._context = kwargs.get('context', 'declare')
        super(Argument, self).__init__(**kwargs)
        assert(self._context != 'keyword' or self._default)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Argument, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['default'] = self._default
        kwargs.update(super(Argument, self).get_kwargs())
        return kwargs

    def OnUndoRedoChanged(self):
        """Update from app"""
        self.parent.OnUndoRedoChanged()
        super(Argument, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self, root=True):
        """Do required actions for removing"""
        super(Argument, self).OnUndoRedoRemoving(root)
        self.parent.OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        self.parent.OnUndoRedoChanged()
        super(Argument, self).OnUndoRedoAdd()

    @property
    def label(self):
        """Get tree label"""
        if self._context == 'declare':
            if self._default:
                return '{self._name}={self._default}'.format(self=self)
            else:
                return self._name
        if self._context == 'value':
            return self._name
        if self._context == 'keyword':
            return '{self._name}={self._default}'.format(self=self)
        if self._context == 'starargs':
            return '*{self._default}'.format(self=self)
        if self._context == 'kwargs':
            return '**{self._default}'.format(self=self)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('py_argument')

