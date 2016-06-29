# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import git
import wx
import model
import os
import os.path
import copy
import app.resources as rc
import app.ui.dlg as dlg
from ctx import localcontext as context


class GitRepo(model.TComponent):
    """Implements git repo representation"""
    folder_container = True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._lastHdrTime = None
        self._lastSrcTime = None
        self._local = kwargs.get('local', True)
        self._uri = kwargs.get('uri', None)
        if not kwargs.get('name', None):
            s = self._uri
            s, t = os.path.split(s)
            if len(t) == 0:
                s, t = os.path.split(s)
            kwargs['name'] = t
        super(GitRepo, self).__init__(**kwargs)
        # The first step is to iterate over the git repository
        # structure to fill it
        working = dlg.WorkingDialog(context.frame)
        working.Show(True)
        wx.YieldIfNeeded()
        self._repo = git.Repo(self._uri)
        model.git.GitRemotes(parent=self)
        self.load_dir()
        working.Close()

    @property
    def stage_size(self):
        """return the number of elements in stage"""
        return len(self._repo.index.entries)

    def commit(self, message):
        """do a commit"""
        self._repo.index.commit(message)
        self._repo.index.write()
        self.update_status()

    def add(self, element):
        """add element to repository"""
        self._repo.index.add([element.rpath])
        self._repo.index.write()
        self.update_status()

    @property
    def repo(self):
        """return the model"""
        return self

    def load_dir(self):
        """Load the head commit and add each entry to repository view"""
        hdir = os.path.realpath(self.path)
        if not os.access(hdir, os.R_OK):
            return False
        kwargs = {'parent': self}
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

    def status(self, path):
        """return the status of the file"""
        status = 'file'
        #check first if the file is under control
        if path not in self._repo.untracked_files:
            status = 'git_file'
            modified = self._repo.index.diff(None)
            for f in modified:
                if path not in [f.a_path, f.b_path]:
                    continue
                #ok, the file is modified
                if not f.b_mode and not f.b_blob and not f.b_path:
                    return 'git_file_deleted'
                else:
                    status = 'git_file_modified'
                    break
            staged = self._repo.index.diff('HEAD')
            for f in staged:
                if path not in [f.a_path, f.b_path]:
                    continue
                #ok, the file is modified
                if not f.b_mode and not f.b_blob and not f.b_path:
                    return 'git_file_deleted'
                else:
                    status = 'git_file_staged'
                    break
        return status

    @property
    def path(self):
        """Access for this element"""
        return self._uri

    @property
    def rpath(self):
        """Access for this element"""
        return ''

    def __getstate__(self):
        """Set pickle context"""
        # The repo object has not pickle support ...
        state = copy.copy(self.__dict__)
        del state['_repo']
        return state

    def __setstate__(self, d):
        """Load pickle context"""
        # The repo object has not pickle support ...
        self.__dict__ = d
        self._repo = git.Repo(self._uri)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {
            'local': self._local,
            'uri': self._uri}
        kwargs.update(super(GitRepo, self).get_kwargs())
        return kwargs

    def update_status(self):
        """update the repository status"""
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
        #update remote status
        for element in self[model.git.GitRemotes]:
            element.update_status()

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(GitRepo, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(GitRepo, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(GitRepo, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(GitRepo, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(GitRepo, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(GitRepo, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(GitRepo, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(GitRepo, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('git_repo')

    @property
    def label(self):
        """Get tree label"""
        return 'repository {self._name}'.format(self=self)



