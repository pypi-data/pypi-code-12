# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import model
import app.resources as rc


class PendingTasks(model.Folder):
    """Clase que representa a las tareas pendientes"""

    task_container = True

    @property
    def status_container(self):
        """return the status container"""
        return self

    def SetStatus(self, element):
        """Set the elements as pending"""
        if type(element) is model.tasks.Task:
            self.SaveState()
            self._status = 'pending'
            self._dateEnd = ''
        for subtask in element[model.tasks.Task]:
            self.SetStatus(subtask)
        for subtask in element[model.tasks.TaskFolder]:
            self.SetStatus(subtask)

    def __init__(self, **kwargs):
        """Inicializacion"""
        if 'name' not in kwargs:
            kwargs['name'] = 'Pending Tasks'
        kwargs['readonly'] = True
        super(PendingTasks, self).__init__(**kwargs)

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(PendingTasks, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(PendingTasks, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(PendingTasks, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(PendingTasks, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(PendingTasks, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(PendingTasks, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(PendingTasks, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(PendingTasks, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('folder_pendings')

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folder_pendings_open")

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)
