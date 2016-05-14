# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
import re
import app.resources as rc
from ctx import theContext as context
import model.decorator as ctx
import model
import tran
from tran import TransactionStack


class Destructor(model.Member):
    """Implements ctor method"""
    context_container = True

    # visual methods
    @tran.TransactionalMethod('move destructor ~{}')
    def drop(self, to):
        """Drops class inside project or another folder """
        target = to.inner_member_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        # the name must be allways the same of the class
        kwargs['name'] = kwargs['parent'].inner_class.name
        self._access = kwargs.get('access', "public")
        self._explicit = kwargs.get('explicit', False)
        self._inline = kwargs.get('inline', False)
        self._virtual = kwargs.get('virtual', True)
        self._pure = kwargs.get('pure', False)
        self._calling = kwargs.get('calling', False)
        self._callingText = kwargs.get('callspec', False)
        self._content = kwargs.get('content', "")
        super(Destructor, self).__init__(**kwargs)
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(Destructor, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['access'] = self._access
        kwargs['explicit'] = self._explicit
        kwargs['inline'] = self._inline
        kwargs['virtual'] = self._virtual
        kwargs['pure'] = self._pure
        kwargs['calling'] = self._calling
        kwargs['callspec'] = self._callingText
        kwargs['content'] = self._content
        kwargs.update(super(Destructor, self).get_kwargs())
        return kwargs

    def UpdateExitCall(self, save=True):
        """Updates the call to exit method"""
        if save:
            self.SaveState()
        method = self.inner_class.exit_methods
        mask = r'\t__exit__\s*\(.*\);\n'
        if not method:
            #if there are not exit method, remove the call
            self._content = re.sub(mask, '', self._content)
            return
        method = method[0]
        #add the call
        if not re.search(mask, self._content):
            self._content = '\t__exit__();\n' + self._content

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the member method declaration"""
        i = self.inner_class
        i._ensure_access(pf, self._access)
        pf.writeln(self.declare)
        if self._inline:
            self.outer_class._inlines.append(self)

    @ctx.ContextImplementation()
    def WriteCode(self, f):
        """Write code to file"""
        self.WriteComment(f)
        f.writeln(self.implement)
        f.openbrace()
        f.writeln(self._content)
        f.closebrace()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Destructor, self).OnUndoRedoChanged()
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            index = book.GetPageIndex(self._pane)
            book.SetPageText(index, self.name)
            book.SetPageBitmap(index, self.GetTabBitmap())
            self._pane.m_editor.SetText(self._content)
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            pane = self._pane
            delattr(self, '_pane')
            # we are not able to commit here!
            # pane.Commit()
            pane.PreDelete()    # avoid gtk-critical
            self._paneIndex = book.GetPageIndex(pane)
            book.DeletePage(self._paneIndex)
        super(Destructor, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Destructor, self).OnUndoRedoAdd()
        if hasattr(self, '_paneIndex'):
            book = context.frame.docBook
            import pane
            p = pane.MethodPane(book, context.frame, self)
            self._pane = p
            book.InsertPage(self._paneIndex, p, self.tab_label,
                False, self.bitmap_index)
            delattr(self, '_paneIndex')

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap("destructor", self._access)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("destructor", self._access)

    @property
    def tree_label(self):
        """Get tree label"""
        epilog = ""
        if self._pure:
            epilog += "=0"
        prolog = ""
        if self._virtual:
            prolog = "virtual "
        if self._inline:
            prolog = prolog + "inline "
        return prolog + "~" + self._name + "()" + epilog

    @property
    def tab_label(self):
        """Get tree label"""
        epilog = ""
        if self._pure:
            epilog += "=0"
        prolog = ""
        if self._virtual:
            prolog = "virtual "
        if self._inline:
            prolog = prolog + "inline "
        return "~{self.name}()".format(self=self)

    @property
    def declare(self):
        """Get declare string"""
        epilog = ""
        if self._pure:
            epilog += "=0"
        prolog = ""
        if self._virtual:
            prolog = "virtual "
        if self._inline:
            prolog = prolog + "inline "
        return "{prolog}~{name}(){epilog};".format(prolog=prolog, name=self._name, epilog=epilog)

    @property
    def implement(self):
        """Gets tab label"""
        return "{self.scope}~{self._name}()".format(self=self)

    def ExistArgumentNamed(self, name):
        """Checks about argument existence"""
        return False


