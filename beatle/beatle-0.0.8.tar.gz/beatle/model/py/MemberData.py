# -*- coding: utf-8 -*-

import model.decorator as ctx
import app.resources as rc
import tran
import model


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
        self._scope = kwargs.get('scope', "class")
        self._value = kwargs.get('value', "")
        super(MemberData, self).__init__(**kwargs)
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()


    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['scope'] = self._scope
        kwargs['value'] = self._value
        kwargs.update(super(MemberData, self).get_kwargs())
        return kwargs

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the member declaration"""
        pass

    @ctx.ContextImplementation()
    def WriteCode(self, pf):
        """Write the member implementation"""
        pass

    def GetInitializer(self):
        """Return the initializer sequence"""
        if len(self._value) > 0:
            return self._value
        return '{self._name}=None'.format(self=self)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_member")

    def Delete(self):
        """Remove object"""
        k = self.inner_module or self.inner_package
        super(MemberData, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(MemberData, self).OnUndoRedoAdd()

    def OnUndoRedoChanged(self):
        """Make changes in the model as result of change"""
        super(MemberData, self).OnUndoRedoChanged()

    def ExportPythonCode(self, wf):
        """Write code"""
        if len(self._value):
            wf.writeln('{self._name} = {self._value}'.format(self=self))
        else:
            wf.writeln('{self._name} = None'.format(self=self))
