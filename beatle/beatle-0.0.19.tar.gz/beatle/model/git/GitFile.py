# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import wx
import model
import os
import os.path
import app.resources as rc


class GitFile(model.TComponent):
    """Implements c++ class representation"""
    folder_container = True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._lastHdrTime = None
        self._lastSrcTime = None
        self._name = kwargs['name']
        self._parent = kwargs['parent']
        #Query the status: the file is modified, staged or deleted?
        self._status = self.repo.status(self.rpath)
        wx.YieldIfNeeded()
        super(GitFile, self).__init__(**kwargs)
        # iterate over the tree
        # assert len(self._data.hexsha) == 40

    @property
    def repo(self):
        """return the repo"""
        return self.parent.repo

    def update_status(self):
        """Update the file status"""
        wx.YieldIfNeeded()
        self._status = self.repo.status(self.rpath)
        self.OnUndoRedoChanged()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {'data': self._data}
        kwargs.update(super(GitFile, self).get_kwargs())
        return kwargs

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(GitFile, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(GitFile, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(GitFile, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(GitFile, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(GitFile, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(GitFile, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #when the class is updated, ctor's and dtors, must be updated
        super(GitFile, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(GitFile, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex(self._status)

    @property
    def path(self):
        """Access for this element"""
        return os.path.join(self.parent.path, self._name)

    @property
    def rpath(self):
        """Access for this element"""
        return os.path.join(self.parent.rpath, self._name)

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)



