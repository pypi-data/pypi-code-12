# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

"""Git remote representation"""

import model
import app.resources as rc


class GitRemotes(model.TComponent):
    """Implements git remotes folder"""

    def __init__(self, **kwargs):
        """Initialization method"""
        self._lastHdrTime = None
        self._lastSrcTime = None
        if 'name' not in kwargs:
            kwargs['name'] = 'remotes'
        self._parent = kwargs['parent']
        super(GitRemotes, self).__init__(**kwargs)
        self.load_remotes()

    def load_remotes(self):
        """Update remotes"""
        kwargs = {'parent': self}
        for remote in self.repo._repo.remotes:
            kwargs['name'] = remote.name
            model.git.GitRemote(**kwargs)

    def update_status(self):
        """update the remote status"""
        old_remotes = dict([(x.name, x) for x in self(model.git.GitRemote)])
        new_remotes = dict([(x.name, x) for x in self.repo._repo.remotes])
        # remove missing remotes
        todel = [old_remotes[x] for x in old_remotes if x not in new_remotes]
        tonew = [new_remotes[x] for x in new_remotes if x not in old_remotes]
        for x in todel:
            x.Delete()
        kwargs = {'parent': self}
        for x in tonew:
            kwargs['name'] = x.name
            model.git.GitRemote(**kwargs)

    @property
    def repo(self):
        """get the local repo object"""
        return self.parent.repo

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {'data': self._data}
        kwargs.update(super(GitRemotes, self).get_kwargs())
        return kwargs

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(GitRemotes, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(GitRemotes, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(GitRemotes, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(GitRemotes, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(GitRemotes, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(GitRemotes, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #when the class is updated, ctor's and dtors, must be updated
        super(GitRemotes, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(GitRemotes, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('git_repo')

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)



