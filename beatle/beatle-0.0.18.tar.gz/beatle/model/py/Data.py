# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""


import model
import app.resources as rc
import tran


class Data(model.TComponent):
    """Implements data"""
    context_container = True

    # visual methods
    @tran.TransactionalMethod('move python variable {}')
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
        self._value = kwargs.get('value', "'None'")
        super(Data, self).__init__(**kwargs)
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def Delete(self):
        """Handle delete"""
        k = self.inner_module or self.inner_package
        super(Data, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['value'] = self._value
        kwargs.update(super(Data, self).get_kwargs())
        return kwargs

    def WriteCode(self, pf):
        """wtite data definition"""
        pass

    def GetInitializer(self):
        """Return the initializer sequence"""
        if len(self._value) > 0:
            return self._value
        return self._name

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_variable")

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Data, self).OnUndoRedoAdd()

    def OnUndoRedoChanged(self):
        """Make changes in the model as result of change"""
        super(Data, self).OnUndoRedoChanged()

    def ExportPythonCode(self, wf):
        """Write code"""
        if len(self._value):
            wf.writeln('{self._name} = {self._value}'.format(self=self))
        else:
            wf.writeln('{self._name} = None'.format(self=self))

