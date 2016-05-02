# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""

import os
import model
import tran
from model.writer import writer
import app.resources as rc
from tran import TransactionStack
from Module import Module


class pyBoostModule(Module):
    """Implements a Module representation"""
    class_container = False
    folder_container = True
    diagram_container = True
    namespace_container = True
    function_container = True
    variable_container = True
    enum_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        self._content = kwargs.get('content')
        self._uids = kwargs.get('uids')
        super(pyBoostModule, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {'content': self._content}
        kwargs.update(super(pyBoostModule, self).get_kwargs())
        return kwargs

    @tran.DelayedMethod
    def ExportCppCodeFiles(self, force=True):
        """Do code generation"""
        self.updateSources(force)

    def WriteCode(self, pf):
        """Write code for module"""
        pf.writeln(self._content)

    def updateSources(self, force=False):
        """does source generation"""
        sources_dir = self.project.sources_dir
        fname = os.path.realpath(os.path.join(sources_dir, self._source))
        if force or not os.path.exists(fname) or self._lastSrcTime is None:
            regenerate = True
        elif os.path.getmtime(fname) < self._lastSrcTime:
            regenerate = True
        project = self.project
        if regenerate:
            with open(fname, 'w') as f:
                pf = writer.for_file(f)
                pf.writeln("// {user.before.include.begin}")
                pf.writenl()
                pf.writeln("// {user.before.include.end}")
                pf.writenl()
                if project._useMaster:
                    pf.writeln('#include "{}"'.format(project._masterInclude))
                    pf.writenl()
                pf.writeln("// {user.before.code.begin}")
                pf.writenl()
                pf.writeln("// {user.before.code.end}")
                pf.writenl()
                self.WriteCode(pf)
                pf.writenl()
                pf.writeln("// {user.after.code.begin}")
                pf.writenl()
                pf.writeln("// {user.after.code.end}")
                pf.writenl()

    def updateHeaders(self, force=False):
        """Realiza la generacion de fuentes"""
        pass

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("pyboost")

    @property
    def inner_class(self):
        """Get the innermost class container"""
        return None

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Module, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            self.project.ExportCppCodeFiles(force=True)
