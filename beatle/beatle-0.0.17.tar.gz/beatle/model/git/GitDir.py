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


class GitDir(model.TComponent):
    """Implements git dir representation"""
    folder_container = True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._lastHdrTime = None
        self._lastSrcTime = None
        self._name = kwargs['name']
        self._parent = kwargs['parent']
        super(GitDir, self).__init__(**kwargs)
        wx.YieldIfNeeded()
        self.load_dir()

    def load_dir(self):
        """Recursively descend and analyse existing files
        for representing it even if they are not under git control"""
        hdir = os.path.realpath(self.path)
        if not os.access(hdir, os.R_OK):
            return False
        for elem in os.listdir(hdir):
            if elem[0] == '.':
                continue
            path = os.path.join(hdir, elem)
            if os.path.isdir(path):
                kwargs = {'name': elem, 'parent': self}
                model.git.GitDir(**kwargs)
            if os.path.isfile(path):
                kwargs = {'name': elem, 'parent': self}
                model.git.GitFile(**kwargs)
            else:
                continue
        return True

    def update_status(self):
        """update the directory status"""
        wx.YieldIfNeeded()
        hdir = os.path.realpath(self.path)
        if not os.access(hdir, os.R_OK):
            return
        dirs = []
        files = []
        for elem in os.listdir(hdir):
            path = os.path.join(hdir, elem)
            if elem[0] == '.':
                continue
            if os.path.isdir(path):
                dirs.append(elem)
            if os.path.isfile(path):
                files.append(elem)
            else:
                continue
        #current
        curdirs = self[model.git.GitDir]
        curfiles = self[model.git.GitFile]
        #new
        newdirs = [x for x in dirs if x not in [y.name for y in curdirs]]
        newfiles = [x for x in files if x not in [y.name for y in curfiles]]
        #delete dirs and files
        deldir = [x for x in curdirs if x.name not in dirs]
        delfile = [x for x in curfiles if x.name not in files]
        for x in deldir:
            x.Delete()
        for x in delfile:
            x.Delete()
        #update existing
        for d in self[model.git.GitDir]:
            d.update_status()
        for f in self[model.git.GitFile]:
            f.update_status()
            f.OnUndoRedoChanged()
        #new files and dirs
        for elem in newdirs:
            model.git.GitDir(name=elem, parent=self)
        for elem in newfiles:
            model.git.GitFile(name=elem, parent=self)
    @property
    def repo(self):
        """get the report object"""
        return self.parent.repo

    @property
    def path(self):
        """Access for this element"""
        return os.path.join(self.parent.path, self._name)

    @property
    def rpath(self):
        """Access for this element"""
        return os.path.join(self.parent.rpath, self._name)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {'data': self._data}
        kwargs.update(super(GitDir, self).get_kwargs())
        return kwargs

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(GitDir, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(GitDir, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(GitDir, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(GitDir, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(GitDir, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(GitDir, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #when the class is updated, ctor's and dtors, must be updated
        super(GitDir, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(GitDir, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('git_repo')

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)



