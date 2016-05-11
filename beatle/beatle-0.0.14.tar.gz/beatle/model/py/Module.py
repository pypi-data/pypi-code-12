# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""

import os
import sys
import traceback
import wx
import model
import analytic
from model.writer import writer
from Import import Import
from ImportsFolder import ImportsFolder
import app.resources as rc
import tran


class Module(model.TComponent):
    """Implements a Module representation"""
    class_container = True
    folder_container = True
    diagram_container = True
    namespace_container = False
    function_container = True
    variable_container = True
    enum_container = False
    import_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        self._lastSrcTime = None
        self._lastHdrTime = None
        self._entry = False
        self._content = kwargs.get('content', "")
        self._file_obj = None  # vincle with file object
        super(Module, self).__init__(**kwargs)
        self.ExportPythonCodeFiles()

    def set_file(self, file_obj):
        """Sets the vincle with file object"""
        self._file_obj = file_obj

    def Delete(self):
        """delete the object"""
        if hasattr(self, '_file_obj') and self._file_obj:
            self._file_obj.Delete()
        super(Module, self).Delete()

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['content'] = self._content
        kwargs.update(super(Module, self).get_kwargs())
        return kwargs

    @property
    def key_file(self):
        """This method returns the key file. For modules, is
        the implementation file. For packages, is the __init__ file."""
        fname = os.path.join(self.dir, '{self._name}.py'.format(self=self))
        return os.path.realpath(fname)

    @property
    def dir(self):
        """return the container dir"""
        return self.parent.dir

    @property
    def path_name(self):
        """Get the full path"""
        if self.parent.inner_module is not None:
            return '{self.parent.inner_module.path_name}.{self._name}'.format(self=self)
        return self._name

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        stack = tran.TransactionStack
        method = self.ExportPythonCodeFiles.inner
        if method not in stack.delayedCallsFiltered:
            stack.delayedCallsFiltered.append(method)
        super(Module, self).OnUndoRedoRemoving()

    def ExportPythonFolderCodeFiles(self, fw, folder, force, logger=None):
        """does python export for folders"""
        for subfolder in folder[model.Folder]:
            self.ExportPythonFolderCodeFiles(fw, subfolder, force, logger)

        for obj in folder[ImportsFolder]:
            obj.ExportPythonCode(fw)

        for obj in folder[Import]:
            obj.ExportPythonCode(fw)

        from Class import Class
        for obj in folder[Class]:
            obj.ExportPythonCode(fw)

        from Function import Function
        for obj in folder[Function]:
            obj.ExportPythonCode(fw)

        from Data import Data
        for obj in folder[Data]:
            obj.ExportPythonCode(fw)

    @property
    def abs_path(self):
        """return the absolute path"""
        return os.path.join(self.dir, '{self._name}.py'.format(self=self))

    @tran.DelayedMethod
    def ExportPythonCodeFiles(self, force=False, logger=None):
        """does source generation"""
        #The mission of this method is to generate the required code
        #for the python
        fname = self.abs_path
        logger and logger.AppendReportLine('exporting module {}'.format(self._name), wx.ICON_INFORMATION)
        try:
            f = open(fname, 'w')
            fw = writer.for_file(f, 'python')

            #first thing: generate module comment
            fw.writeln("# -*- coding: utf-8 -*-")
            fw.writecomment(self._note)
            fw.writenl()

            #we have some problem here with the order the code is generated
            #for solving that, we use nested folders
            for folder in self[model.Folder]:
                self.ExportPythonFolderCodeFiles(fw, folder, force, logger)

            #declare the orderer collections of things
            #that would be exported

            #fw.writeln("#imports")
            for obj in self[ImportsFolder]:
                obj.ExportPythonCode(fw)
            for obj in self[Import]:
                obj.ExportPythonCode(fw)

            from Class import Class
            for obj in self[Class]:
                obj.ExportPythonCode(fw)

            from Function import Function
            for obj in self[Function]:
                obj.ExportPythonCode(fw)

            from Data import Data
            for obj in self[Data]:
                obj.ExportPythonCode(fw)

            #At last, write raw code
            fw.writenl(1)
            fw.writeln("#raw code")
            fw.writeblock(self._content)

            f.close()

        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            if logger:
                logger.AppendReportLine('failed opening {}'.format(fname), wx.NOT_FOUND)
            return False

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap("py_module")

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_module")

    @property
    def inner_class(self):
        """Get the innermost class container"""
        return None

    def analize(self):
        """Do an analisis of the raw content and extracts
        whatever its possible to extract"""
        self.DeleteChilds()
        s = analytic.pyparse(self, self._content)
        self._content = s.inline()
        return s._status

    @property
    def locals(self):
        """This method returns all the top elements defined
        in the module"""
        f = lambda x: x.inner_module == self
        raw = self(model.py.Class, model.py.Data, model.py.Function, filter=f)
        return dict([(e._name, e) for e in raw])

    def _local_import(self, name):
        """This method finds for a module or package (in this order)
        matching the name of the import, inside the same directory of
        the module. Please take consideration of that
        the name must be simple, without dots. Returns the module or package
        or None if not found"""
        container = self.inner_package
        f = lambda x: x != self and x.inner_package == container
        for x in self(model.py.Module, filter=f, cut=True):
            if x._name == name:
                return x
        f = lambda x: x.parent.inner_package == container
        for x in self(model.py.Package, filter=f, cut=True):
            if x._name == name:
                return x
        return None

    def _global_import(self, name):
        """This method finds for a module or package (in this order)
        matching the name of the import, inside the root directory of
        the project. Please take consideration of that
        the name must be simple, without dots. Returns the module or package
        or None if not found"""
        f = lambda x: x != self and x.inner_package is None
        for x in self(model.py.Module, filter=f, cut=True):
            if x._name == name:
                return x
        f = lambda x: x.parent.inner_package is None
        for x in self(model.py.Package, filter=f, cut=True):
            if x._name == name:
                return x
        return None

    def _import(self, name, root=True):
        """Get the import (if possible)"""
        sections = name.split('.')
        if not len(sections):
            return None
        base = sections[0]
        del sections[0]
        base = self._local_import(base) or self._global_import(base)
        if base is None:
            #this import is external
            import ostools
            return ostools.import_dir(name)
        for next in sections:
            base = base._local_import(next)
            if base is None:
                return None
        return base

    @property
    def globals(self):
        """This method returns all the globals 'visible' inside the module"""
        # basicly we iterate through the imports
        f = lambda x: x.inner_module == self
        imports = self(model.py.Import, filter=f)
        #
        d = {}
        for imp in imports:
            # buscamos el modulo o fuente que se importa.
            m = self._import(imp._name)
            if m is None:
                #pending log failed import
                continue
            # m puede ser un Module, un Package o bien una lista de simbolos
            # procedentes de una importacion nativa
            if imp._from is not None:
                #en este caso lo que se importa es un simbolo
                #buscamos el simbolo
                if type(m) is list:
                    if imp._from not in m:
                        # pending log misssing symbol
                        continue
                    symbol = m[imp._from]
                elif type(m) is model.py.Package:
                    symbol = m._local_import(imp._from)
                    if imp._from not in m:
                        # pending log misssing symbol
                        continue
                    symbol = m[imp._from]
                elif type(m) is model.py.Module:
                    l = m.locals()
                    l.extend(m.globals())
                    if imp._from not in l:
                        #pending log missing symbol
                        continue
                    symbol = l[imp._from]
            else:
                symbol = m
            if imp._as:
                d[imp._as] = symbol
            else:
                d[imp._name] = symbol
        return d

