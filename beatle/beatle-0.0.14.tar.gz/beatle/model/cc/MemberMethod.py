# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""
import wx
import model
import app.resources as rc
from ctx import theContext as context
import model.decorator as ctx
import tran
from tran import TransactionStack


class MemberMethod(model.Member):
    """Implements member method"""
    context_container = True
    argument_container = True

    # visual methods
    def draggable(self):
        """returns info about if the object can be moved"""
        return True

    @tran.TransactionalMethod('move method {}')
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
        self._typei = kwargs['type']
        self._access = kwargs.get('access', 'public')
        self._static = kwargs.get('static', False)
        self._virtual = kwargs.get('virtual', False)
        self._pure = kwargs.get('pure', False)
        self._inline = kwargs.get('inline', False)
        self._const_method = kwargs.get('constmethod', False)
        self._content = kwargs.get('content', "")
        self._template = kwargs.get('template', None)
        self._template_types = kwargs.get('template_types', [])
        super(MemberMethod, self).__init__(**kwargs)
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(MemberMethod, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['type'] = self._typei
        kwargs['access'] = self._access
        kwargs['static'] = self._static
        kwargs['virtual'] = self._virtual
        kwargs['pure'] = self._pure
        kwargs['inline'] = self._inline
        kwargs['constmethod'] = self._const_method
        kwargs['content'] = self._content
        kwargs['template'] = self._template
        kwargs['template_types'] = self._template_types
        kwargs.update(super(MemberMethod, self).get_kwargs())
        return kwargs

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the member method declaration"""
        if self._declare:
            i = self.inner_class
            i._ensure_access(pf, self._access)
            pf.writeln(self.declare)
            if self._inline or i._template or self._template:
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
        super(MemberMethod, self).OnUndoRedoChanged()
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            index = book.GetPageIndex(self._pane)
            book.SetPageText(index, self.name)
            book.SetPageBitmap(index, self.GetTabBitmap())
            if self._pane.m_editor.GetText() != self._content:
                self._pane.m_editor.SetText(self._content)
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            p = self._pane
            delattr(self, '_pane')
            # we are not able to commit here!
            # pane.Commit()
            p.PreDelete()    # avoid gtk-critical
            self._paneIndex = book.GetPageIndex(p)
            book.DeletePage(self._paneIndex)
        super(MemberMethod, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        import pane
        super(MemberMethod, self).OnUndoRedoAdd()
        if hasattr(self, '_paneIndex'):
            book = context.frame.docBook
            p = pane.MethodPane(book, context.frame, self)
            self._pane = p
            book.InsertPage(self._paneIndex, p, self.tab_label,
                False, wx.NOT_FOUND)
            book.SetPageBitmap(self._paneIndex, self.GetTabBitmap())
            delattr(self, '_paneIndex')

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap("method", self._access)

    @property
    def type_instance(self):
        """return the type instance"""
        return self._typei

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("method", self._access)

    @property
    def tree_label(self):
        """Get tree label"""
        if self._template:
            stype = 'template<{}> '.format(self._template)
        else:
            stype = ''
            if self._virtual:
                stype = "virtual "
            if self._inline:
                stype = "inline " + stype
        stype += str(self._typei)
        from Argument import Argument
        argl = ', '.join(arg.declare for arg in self[Argument])
        epilog = ""
        if self._pure:
            epilog += "=0"
        if self._const_method:
            epilog += " const"
        return stype.format(self._name + "(" + argl + ")") + epilog

    @property
    def call(self):
        """Call default expression"""
        from Argument import Argument
        argl = ', '.join(arg.name for arg in self[Argument])
        return "{name}({argl})".format(name=self.name, argl=argl)

    @property
    def tab_label(self):
        """Get tab label"""
        from Argument import Argument
        argl = ', '.join(arg.implement for arg in self[Argument])
        return "{name}({argl})".format(name=self.name, argl=argl)

    @property
    def implement(self):
        """Gets tab label"""
        from Argument import Argument
        if self._template:
            s = 'template<{}> '.format(self._template)
        elif self._virtual:
            s = "virtual "
        else:
            s = ''
        if self._inline:
            s = "inline " + s
        s += str(self._typei)
        argl = ', '.join(arg.implement for arg in self[Argument])
        epilog = ""
        if self._const_method:
            epilog += " const"
        untyped = '{self.scope}{self._name}({args})'.format(self=self, args=argl)
        return s.format(untyped) + epilog

    @property
    def declare(self):
        """declaration string inside class"""
        from Argument import Argument
        if self._template:
            s = 'template<{}> '.format(self._template)
        elif self._virtual:
            s = "virtual "
        else:
            s = ''
        if self._inline:
            s = "inline " + s
        s += str(self._typei)
        argl = ', '.join(arg.declare for arg in self[Argument])
        epilog = ""
        if self._pure:
            epilog += "=0"
        if self._const_method:
            epilog += " const"
        untyped = '{self._name}({args}){epilog}'.format(self=self, args=argl, epilog=epilog)
        return s.format(untyped) + ";"

    def ExistArgumentNamed(self, name):
        """Returns information about argument existence"""
        from Argument import Argument
        return self.hasChild(name=name, type=Argument)

    @property
    def template_types(self):
        """Returns the list of nested template types"""
        # _template_types are locally applied/defined and will override outer
        # template types (of course in any moment we need to alert from that).
        lt = self._template_types
        nt = super(MemberMethod, self).template_types
        lt.extend([x for x in nt if x not in self._template_types])
        return lt

