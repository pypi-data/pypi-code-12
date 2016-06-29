# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""
import model.decorator as ctx
import app.resources as rc
import tran
import model
from tran import TransactionStack


class MemberData(model.Member):
    """Implements member data"""
    context_container = True

    # visual methods
    @tran.TransactionalMethod('move member {}')
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
        "Initialization"
        self._typei = kwargs['type']
        self._access = kwargs.get('access', "public")
        self._static = kwargs.get('static', False)
        self._volatile = kwargs.get('volatile', False)
        self._mutable = kwargs.get('mutable', False)
        self._bitField = kwargs.get('bitfield', False)
        self._bitFieldSize = kwargs.get('bitfieldsize', 0)
        self._default = kwargs.get('default', "")
        super(MemberData, self).__init__(**kwargs)
        if kwargs.get('update_ctors', True):
            self.inner_class.AutoArgs()
            self.inner_class.AutoInit()
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(MemberData, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['type'] = self._typei
        kwargs['access'] = self._access
        kwargs['static'] = self._static
        kwargs['volatile'] = self._volatile
        kwargs['mutable'] = self._mutable
        kwargs['bitfield'] = self._bitField
        kwargs['bitfieldsize'] = self._bitFieldSize
        kwargs['default'] = self._default
        kwargs.update(super(MemberData, self).get_kwargs())
        return kwargs

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the member declaration"""
        self.inner_class._ensure_access(pf, self._access)
        self.WriteComment(pf)
        pf.writeln("{};".format(self.label))

    @ctx.ContextImplementation()
    def WriteCode(self, pf):
        """Write the member implementation"""
        if self._static:
            pf.writeln("{};".format(self.GetStaticDefinition()))

    def GetInitializer(self):
        """Return the initializer sequence"""
        if len(self._default) > 0:
            return self._default
        return self._name

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("member", self._access)

    def GetStaticDefinition(self):
        """Return global, static definition"""
        if not self._static:
            return ""
        stype = self._typei.scoped_str([self.inner_class.scope])
        if self._volatile:
            stype = "volatile " + stype
        if self._mutable:
            stype = "mutable " + stype
        #if self._static:
        #    stype = "static " + stype
        epi = ""
        if self._bitField:
            epi = ":" + str(self._bitFieldSize)
        mname = self.inner_class._memberPrefix + self._name
        return stype.format('{self.scope}::{mname}{epi}'.format(
            self=self, mname=mname, epi=epi)) + ' = ' + self._default

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(MemberData, self).OnUndoRedoAdd()

    def OnUndoRedoChanged(self):
        """Make changes in the model as result of change"""
        super(MemberData, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    @property
    def label(self):
        """Get tree label"""
        s = ''
        s = self._typei.scoped_str([self.inner_class.scope])
        if self._volatile:
            s = "volatile " + s
        if self._mutable:
            s = "mutable " + s
        if self._static:
            s = "static " + s
        epi = ""
        if self._bitField:
            epi = ":" + str(self._bitFieldSize)
        return s.format(self.prefixed_name) + " " + epi

    @property
    def prefixed_name(self):
        """local var name, with class prefix"""
        return self.inner_class._memberPrefix + self._name

    @property
    def type_instance(self):
        """return the type instance"""
        return self._typei
