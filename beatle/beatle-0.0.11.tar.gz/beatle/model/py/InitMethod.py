# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
import app.resources as rc
import model.decorator as ctx
import tran
from MemberMethod import MemberMethod


class InitMethod(MemberMethod):
    """Implements member method"""

    # visual methods
    @tran.TransactionalMethod('move init method {}')
    def drop(self, to):
        """Drops datamember inside project or another folder """
        target = to.inner_member_container
        if not target or self.inner_class != target.inner_class or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs["static_method"] = False
        kwargs["class_method"] = False
        kwargs["property"] = False
        kwargs["name"] = '__init__'
        super(InitMethod, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(InitMethod, self).get_kwargs())
        del kwargs['static_method']
        del kwargs['class_method']
        del kwargs['property']
        return kwargs

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the member method declaration"""
        pass

    @ctx.ContextImplementation()
    def WriteCode(self, f):
        """Write code to file"""
        pass

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(InitMethod, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        super(InitMethod, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(InitMethod, self).OnUndoRedoAdd()

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap("py_init")

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_init")

    @property
    def tree_label(self):
        """Get tree label"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        alist = ', '.join(arg.label for arg in
            self[Argument] + self[ArgsArgument] + self[KwArgsArgument])
        return '__init__({arglist})'.format(arglist=alist)

    def ExistArgumentNamed(self, name):
        """Check about the existence of an argument"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        return name in [x._name for x in self(Argument, ArgsArgument, KwArgsArgument)]

