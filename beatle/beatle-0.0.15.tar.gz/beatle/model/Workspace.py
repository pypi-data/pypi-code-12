# -*- coding: utf-8 -*-

import copy
import app.resources as rc
from ctx import theContext as context
import model.TComponent


class Workspace(model.TComponent):
    """Representation of Workspace"""

    #class_container = False
    #folder_container = False
    #diagram_container = True
    #module_container = False
    #namespace_container = False
    project_container = True
    repository_container = True

    def __init__(self, **kwargs):
        """Initialization of workspace"""
        self._dir = kwargs['dir']
        self._author = kwargs.get('author', "<unknown>")
        self._date = kwargs.get('date', "08-10-2966")
        self._license = kwargs.get('license', None)
        self._modified = True
        self._lastHdrTime = None
        super(Workspace, self).__init__(**kwargs)

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        super(Workspace, self).OnUndoRedoRemoving(root)
        #context.app.RemoveWorkspace(self)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        context.app.AddWorkspace(self)
        super(Workspace, self).OnUndoRedoAdd()

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap('workspace')

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('workspace')

    def __getstate__(self):
        """Set pickle context"""
        # we dont want to serialize projects directly
        state = copy.copy(self.__dict__)
        state['_child'] = copy.copy(self._child)
        state['_child'][model.Project] = [
            (x._dir.replace("//", "/") + "/" + x._name + ".pcc").replace("//", "/")
            for x in self[model.Project] if type(x) is model.Project]
        return state

    def __setstate__(self, d):
        """Load pickle context"""
        plist = d['_child'].get(model.Project, None)
        if plist:
            del d['_child'][model.Project]
        self.__dict__ = d
        if plist:
            for pf in plist:
                context.app.LoadProject(pf, self)

    def SetModified(self, bModified=True):
        """Set the modified state"""
        self._lastHdrTime = None
        self._modified = bModified

    def IsModified(self):
        """Get the modified state"""
        return self._modified