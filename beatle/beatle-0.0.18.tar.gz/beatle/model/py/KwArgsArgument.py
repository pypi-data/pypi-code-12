# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

import model
import tran
import app.resources as rc
from Argument import Argument


class KwArgsArgument(Argument):
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
        kwargs['name'] = 'kwargs'
        kwargs['default'] = ''
        super(KwArgsArgument, self).__init__(**kwargs)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('py_kwargs')
        #return 5

    @property
    def label(self):
        """Get tree label"""
        return '**{self._name}'.format(self=self)
