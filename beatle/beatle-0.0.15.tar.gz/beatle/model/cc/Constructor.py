# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:08:46 2013

@author: mel
"""


import copy
import re
import wx
import model
import model.decorator as ctx
import tran


from ctx import theContext as context
import app.resources as rc


class Constructor(model.Member):
    """Implements ctor method"""
    context_container = True
    argument_container = True

    # visual methods
    @tran.TransactionalMethod('move constructor {}')
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
        self._calling = kwargs.get('calling', False)
        self._callingText = kwargs.get('callspec', False)
        self._init = kwargs.get('init', "")
        self._content = kwargs.get('content', "")
        self._preferred = kwargs.get('preferred', False)
        self._initTouched = False
        self._argsTouched = False
        self._bodyTouched = False
        self._template = kwargs.get('template', None)
        self._template_types = kwargs.get('template_types', [])
        super(Constructor, self).__init__(**kwargs)
        if kwargs.get('autoargs', True):
            self.AutoArgs()
            self.AutoInit(False)
            self.UpdateInitCall(False)
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(Constructor, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['access'] = self._access
        kwargs['explicit'] = self._explicit
        kwargs['inline'] = self._inline
        kwargs['calling'] = self._calling
        kwargs['callspec'] = self._callingText
        kwargs['init'] = self._init
        kwargs['content'] = self._content
        kwargs['preferred'] = self._preferred
        kwargs.update(super(Constructor, self).get_kwargs())
        return kwargs

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the ctor declaration"""
        self.inner_class._ensure_access(pf, self._access)
        pf.writeln(self.declare)
        if self._inline:
            self.outer_class._inlines.append(self)

    def AutoArgs(self):
        """Computes required arguments"""
        if self._argsTouched:
            return
        s = copy.copy(self[model.cc.Argument])
        for arg in s:
            arg.Delete()
        args = self.inner_class.GetClassArguments()
        used = []
        for x in args:
            if x._name in used:
                continue
            used.append(x._name)
            if type(x) is model.cc.RelationFrom:
                ti = model.cc.typeinst(type=x.GetTo().parent, ref=True, const=True)
            else:
                ti = copy.copy(x._typei)
            model.cc.Argument(parent=self, name=x._name, type=ti)

    def UpdateInitCall(self, save=True):
        """Updates the call to init method"""
        if save:
            self.SaveState()
        method = self.inner_class.init_methods
        mask = r'\t__init__\s*\(.*\);\n'
        if not method:
            #if there are not init methods, remove the call
            self._content = re.sub(mask, '', self._content)
            return
        method = method[0]
        #create the call
        callstr = '\t__init__('
        for arg in method[model.cc.Argument]:
            callstr += arg._name + ','
        callstr = callstr[:-1] + ');\n'
        #we need to find the method call
        if re.search(mask, self._content):
            self._content = re.sub(mask, callstr, self._content)
        else:
            self._content = callstr + self._content

    def AutoInit(self, save=True):
        """Computes the init segment"""
        if self._initTouched:
            return
        if save:
            self.SaveState()
        # get inheritence classes
        cls = self.inner_class
        self_cls = lambda x: x.inner_class == cls
        inh = [x._ancestor for x in cls(model.cc.Inheritance, filter=self_cls, cut=True)]
        # get the virtual base classes
        vinh = cls.virtual_bases
        # remove virtuals from normal inheritance
        inh = [x for x in inh if x not in vinh]
        #create a line array
        l = []
        if len(vinh) > 0:
            # l.append("\t//virtual inheritances")
            for x in vinh:
                ctor = x.GetPreferredConstructor()
                s = ''
                if ctor is not None:
                    for arg in ctor[model.cc.Argument]:
                        if len(s) > 0:
                            s = s + ",{}".format(arg._name)
                        else:
                            s = s + arg._name
                l.append("\t{}({})".format(x._name, s))
        if len(inh) > 0:
            # l.append("\t//direct bases")
            for x in inh:
                ctor = x.GetPreferredConstructor()
                s = ''
                if ctor is not None:
                    for arg in ctor[model.cc.Argument]:
                        if len(s) > 0:
                            s = s + ",{}".format(arg._name)
                        else:
                            s = s + arg._name
                l.append("\t{}({})".format(x._name, s))
        #ok, now initialize members
        members = cls(model.cc.MemberData, filter=lambda x: self_cls(x) and not x._static)
        if len(members) > 0:
            # l.append("\t//data members")
            for x in members:
                l.append("\t{}({})".format(cls._memberPrefix + x._name,
                    x.GetInitializer()))
        #Ok, now, generate initialization
        self._init = ''
        sep = ':'
        for s in l:
            self._init += "{}{}\n".format(sep, s)
            sep = ','
        #Update visuals
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            index = book.GetPageIndex(self._pane)
            book.SetPageText(index, self.tab_label)
            book.SetPageBitmap(index, self.GetTabBitmap())
            self._pane.m_init.SetText(self._init)

    def SetSerial(self, flag):
        """Set the serial flag indicating that this is a serializer ctor"""
        if flag:
            cl = self.inner_class.GetSerialConstructor()
            assert cl is None or cl is self
        self._serial = flag

    def SetPreferred(self, flag):
        """Set the preferred flag"""
        if flag:
            # if any one ctor has preferred flag, simply
            # save his state and change
            cls = self.inner_class
            criteria = lambda x: x.inner_class == cls and x._preferred
            pre = cls(model.cc.Constructor, filter=criteria)
            assert len(pre) < 2
            if len(pre):
                pre[0].SaveState()
                pre[0]._preferred = False
        self._preferred = flag

    def IsPreferred(self):
        """Get the preferred flag"""
        return self._preferred

    @ctx.ContextImplementation()
    def WriteCode(self, f):
        """Write code to file"""
        self.WriteComment(f)
        f.writeln(self.implement)
        if len(self._init) > 0:
            f.writeln(self._init)
        f.openbrace()
        f.writeln(self._content)
        f.closebrace()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Constructor, self).OnUndoRedoChanged()
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            index = book.GetPageIndex(self._pane)
            book.SetPageText(index, self.name)
            book.SetPageBitmap(index, self.GetTabBitmap())
            if self._pane.m_init.GetText() != self._init:
                self._pane.m_init.SetText(self._init)
            if self._pane.m_editor.GetText() != self._content:
                self._pane.m_editor.SetText(self._content)
        if not tran.TransactionStack.InUndoRedo():
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
        super(Constructor, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Constructor, self).OnUndoRedoAdd()
        if hasattr(self, '_paneIndex'):
            book = context.frame.docBook
            from pane.ConstructorPane import ConstructorPane
            pane = ConstructorPane(book, context.frame, self)
            self._pane = pane
            book.InsertPage(self._paneIndex, pane, self.tab_label,
                False, self.bitmap_index)
            delattr(self, '_paneIndex')

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        from app.resources import GetBitmap
        return GetBitmap("constructor", self._access)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('constructor', self._access)

    @property
    def tree_label(self):
        """Get tree label"""
        from Argument import Argument
        argl = ', '.join(arg.label for arg in self[Argument])
        prolog = (self._inline and "inline ") or ""
        return '{prolog}{name}({argl})'.format(prolog=prolog, name=self._name, argl=argl)

    @property
    def tab_label(self):
        """Get tree label"""
        from Argument import Argument
        argl = ', '.join(arg.label for arg in self[Argument])
        return '{name}({argl})'.format(name=self._name, argl=argl)

    @property
    def declare(self):
        """Get the string for declaration."""
        from Argument import Argument
        argl = ', '.join(arg.declare for arg in self[Argument])
        return '{self._name}({args});'.format(
            self=self, args=argl)

    @property
    def implement(self, no_default=False):
        """Get the string for implementation"""
        from Argument import Argument
        argl = ', '.join(arg.implement for arg in self[Argument])
        return '{self.scope}{self._name}({args})'.format(
            self=self, args=argl)

    def ExistArgumentNamed(self, name):
        """Returns information about argument existence"""
        from Argument import Argument
        return self.hasChild(name=name, type=Argument)

    @property
    def template_types(self):
        """Returns the list of nested template types"""
        # we need to add types from template nested classes
        lt = self._template_types
        nt = super(Constructor, self).template_types
        lt.extend([x for x in nt if x not in self._template_types])
        return lt

        self._argsTouched = False
        self._bodyTouched = False

    def __setstate__(self, d):
        """Load pickle context.
        This will add some missing attributes in previous releases."""
        d['_argsTouched'] = d.get('_argsTouched', False)
        d['_bodyTouched'] = d.get('_bodyTouched', False)
        self.__dict__ = d
