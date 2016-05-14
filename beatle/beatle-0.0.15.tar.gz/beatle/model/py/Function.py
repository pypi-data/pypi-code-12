# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
import wx
import model
import app.resources as rc
from ctx import theContext as context
import tran


class Function(model.TComponent):
    """Implements member function"""
    context_container = True
    argument_container = True

    # visual methods
    @tran.TransactionalMethod('move function {}')
    def drop(self, to):
        """Drops datamember inside project or another folder """
        target = to.inner_function_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        self._content = kwargs.get('content', "")
        super(Function, self).__init__(**kwargs)
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Function, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['content'] = self._content
        kwargs.update(super(Function, self).get_kwargs())
        return kwargs

    def WriteCode(self, f):
        """Write code to file"""
        pass

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Function, self).OnUndoRedoChanged()
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            index = book.GetPageIndex(self._pane)
            book.SetPageText(index, self.tab_label)
            #book.SetPageBitmap(index, self.GetTabBitmap())
            if self._pane.m_editor.GetText() != self._content:
                self._pane.m_editor.SetText(self._content)

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            p = self._pane
            delattr(self, '_pane')
            p.Commit()
            p.PreDelete()    # avoid gtk-critical
            self._paneIndex = book.GetPageIndex(p)
            book.DeletePage(self._paneIndex)
        super(Function, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        from activity.models.ui import pane
        super(Function, self).OnUndoRedoAdd()
        if hasattr(self, '_paneIndex'):
            book = context.frame.docBook
            p = pane.PyMethodPane(book, context.frame, self)
            self._pane = p
            book.InsertPage(self._paneIndex, p, self.tab_label,
                False, self.bitmap_index)
            delattr(self, '_paneIndex')

    def ExportPythonCode(self, wf):
        """Write code"""
        for deco in self[model.py.Decorator]:
            deco.ExportPythonCode(wf)
        wf.openbrace(self.declare)
        wf.writecomment(self._note)
        wf.writeblock(self._content)
        wf.closebrace()
        wf.writenl()

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap("py_function")

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_function")

    @property
    def tree_label(self):
        """Get tree label"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        alist = ', '.join(arg.label for arg in
            self[Argument] + self[ArgsArgument] + self[KwArgsArgument])
        return '{self._name}({alist})'.format(self=self, alist=alist)

    @property
    def tab_label(self):
        """Get tab label"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        alist = ', '.join(arg.label for arg in
            self[Argument] + self[ArgsArgument] + self[KwArgsArgument])
        return '{self._name}({alist})'.format(self=self, alist=alist)

    @property
    def declare(self):
        """Get tree label"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        alist = ', '.join(arg.label for arg in
            self[Argument] + self[ArgsArgument] + self[KwArgsArgument])
        return 'def {self._name}({alist}):'.format(self=self, alist=alist)

    #def GetFullLabel(self):
    #    """Gets tab label"""
    #    return self.label

    def ExistArgumentNamed(self, name):
        """Returns information about argument existence"""
        from Argument import Argument
        from ArgsArgument import ArgsArgument
        from KwArgsArgument import KwArgsArgument
        return name in [x._name for x in self(Argument, ArgsArgument, KwArgsArgument)]

