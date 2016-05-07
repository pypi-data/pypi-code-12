# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""


import model
import app.resources as rc
import tran
from tran import TransactionStack


class Data(model.TComponent):
    """Implements data"""
    context_container = True

    # visual methods
    @tran.TransactionalMethod('move variable {}')
    def drop(self, to):
        """Drops datamember inside project or another folder """
        target = to.inner_variable_container
        if not target:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        "Initialization"
        self._typei = kwargs['type']
        self._static = kwargs.get('static', False)
        self._volatile = kwargs.get('volatile', False)
        self._default = kwargs.get('default', "")
        super(Data, self).__init__(**kwargs)
        k = self.outer_class or self.outer_module
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module
        super(Data, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['type'] = self._typei
        kwargs['access'] = self._access
        kwargs['static'] = self._static
        kwargs['volatile'] = self._volatile
        kwargs['default'] = self._default
        kwargs.update(super(Data, self).get_kwargs())
        return kwargs

    def WriteCode(self, pf):
        """wtite data definition"""
        pf.writeln("{};".format(self.label))

    def GetInitializer(self):
        """Return the initializer sequence"""
        if len(self._default) > 0:
            return self._default
        return self._name

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("data")

    def GetStaticDefinition(self):
        """Return global, static definition"""
        if not self._static:
            return ''
        stype = str(self._typei)
        if self._volatile:
            stype = "volatile " + stype
        decl = stype.format(self.scoped_name)
        return '{decl} = {value}'.format(decl, self._default)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Data, self).OnUndoRedoAdd()

    def OnUndoRedoChanged(self):
        """Make changes in the model as result of change"""
        super(Data, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    @property
    def label(self):
        """Get tree label"""
        s = ''
        s = str(self._typei)
        if self._volatile:
            s = "volatile " + s
        if self._static:
            s = "static " + s
        epi = ""
        return s.format(self._name) + " " + epi

    @property
    def scope(self):
        """Returns the scope string ie <namespace>::<namespace>::...::
           Returns empty string instead of '::' """
        return self.parent.scope

