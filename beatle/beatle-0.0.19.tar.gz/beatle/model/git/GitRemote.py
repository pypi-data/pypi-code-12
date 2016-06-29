# -*- coding: utf-8 -*-

"""Git remote representation"""

import model
import app.resources as rc


class GitRemote(model.TComponent):
    """Implements git remote representation"""

    def __init__(self, **kwargs):
        """Initialization method"""
        self._url = kwargs.get('url', None)
        self._pass = kwargs.get('pass', None)
        super(GitRemote, self).__init__(**kwargs)
        if kwargs.get('new', False):
            try:
                # The remote repo must be added
                self.repo._repo.create_remote(self._name, self._url)
            except:
                pass

    def update_status(self):
        """update the remote status"""
        pass

    @property
    def repo(self):
        """get the local repo object"""
        return self.parent.repo

    @property
    def password(self):
        """return password"""
        return self._pass

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {'url': self._url, 'pass': self._pass}
        kwargs.update(super(GitRemote, self).get_kwargs())
        return kwargs

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(GitRemote, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        _repo = self.repo._repo
        try:
            ref = _repo.remote(self.name)
            _repo.delete_remote(ref)
        except:
            pass
        super(GitRemote, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(GitRemote, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(GitRemote, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(GitRemote, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        _repo = self.repo._repo
        try:
            ref = _repo.remote(self.name)
            _repo.delete_remote(ref)
        except:
            pass
        super(GitRemote, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #when the class is updated, ctor's and dtors, must be updated
        super(GitRemote, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        try:
            self.repo._repo.create_remote(self._name, self._url)
        except:
            pass
        super(GitRemote, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('git_remote')

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)



