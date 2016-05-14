# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""

import os
import sys
import wx
import model
from ctx import theContext as context
from model.writer import writer
import app.resources as rc
import traceback
import tran


class Package(model.TComponent):
    """Implements a Module representation"""
    class_container = True
    folder_container = True
    diagram_container = True
    namespace_container = False
    function_container = True
    variable_container = True
    enum_container = False
    import_container = True
    package_container = True
    module_container = True

    def __init__(self, **kwargs):
        """Initialization"""
        self._lastSrcTime = None
        self._lastHdrTime = None
        self._entry = False
        self._file_obj = None  # vincle with file object
        super(Package, self).__init__(**kwargs)
        # La forma mas simple de hacer las cosas bien
        # no es pasar menos trabajo. Creamos el modulo __init__
        if not kwargs.get('noinit', False):
            model.py.Module(parent=self, name='__init__', readonly=True)
        self.ExportPythonCodeFiles()

    def set_file(self, file_obj):
        """Sets the vincle with file object"""
        self._file_obj = file_obj

    def Delete(self):
        """delete the object"""
        if hasattr(self, '_file_obj') and self._file_obj:
            self._file_obj.Delete()
        super(Package, self).Delete()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Package, self).get_kwargs()

    @property
    def key_file(self):
        """This method returns the key file. For modules, is
        the implementation file. For packages, is the __init__ file."""
        fname = os.path.join(self.dir, '__init__.py')
        return os.path.realpath(fname)

    @property
    def dir(self):
        """returns the absolute path"""
        d = os.path.join(self.parent.dir, self._name)
        return os.path.realpath(d)

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        stack = tran.TransactionStack
        method = self.ExportPythonCodeFiles.inner
        if method not in stack.delayedCallsFiltered:
            stack.delayedCallsFiltered.append(method)
        super(Package, self).OnUndoRedoRemoving()

    @property
    def abs_path(self):
        """return the absolute path of __init__"""
        return os.path.join(self.dir, '__init__.py'.format(self=self))

    @tran.DelayedMethod
    def ExportPythonCodeFiles(self, force=False, logger=None):
        """does source generation"""
        # Any package is just a directory. And an init file
        package_dir = self.dir
        logger and logger.AppendReportLine('exporting package {}'.format(self._name), wx.ICON_INFORMATION)
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)
            if not os.path.exists(package_dir):
                e = "Failed creating package directory " + package_dir
                if logger is not None:
                    logger.AppendReportLine(e, wx.ICON_ERROR)
                else:
                    wx.MessageBox(e, "Error",
                        wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return False
        #write the init file
        init_file = self.abs_path
        try:
            f = open(init_file, 'w')
            fw = writer.for_file(f, 'python')

            #first thing: generate module comment
            fw.writeln("# -*- coding: utf-8 -*-")
            fw.writecomment(self._note)

            fw.writenl()
            #declare the orderer collections of things
            #that would be exported
            from Import import Import
            from Data import Data
            from Function import Function
            from Class import Class

            # write explicit imports
            fw.writeln("#imports")
            for obj in self[Import]:
                obj.ExportPythonCode(fw)

            #now, for all the exported classes not inside nested package
            package_element = lambda x: x.inner_package == self
            for obj in self(Class, filter=package_element, cut=True):
                if not obj._export:
                    continue
                fw.writeln("from {obj.file_container} import {obj.context_name}".format(obj=obj))

            top = lambda x: not x.inner_module and not x.parent.inner_class
            fw.writenl(2)
            fw.writeln("#data")
            for obj in self(Data):
                obj.ExportPythonCode(fw)

            fw.writenl(2)
            fw.writeln("#functions")
            for obj in self(Function):
                obj.ExportPythonCode(fw)

            fw.writenl(2)
            fw.writeln("#classes")
            for obj in self(Class, filter=top, cut=True):
                obj.ExportPythonCode(fw)
            f.close()

        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            if logger:
                logger.AppendReportLine('failed opening {}'.format(init_file), wx.NOT_FOUND)
            return False

        # do the same as for projects

        for obj in self.packages:
            if obj.parent.inner_package != self:
                continue
            obj.ExportPythonCodeFiles(force, logger)
        for obj in self.modules:
            if obj.parent.inner_package != self:
                continue
            obj.ExportPythonCodeFiles(force, logger)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("py_package")

    def _local_import(self, name):
        """This method finds for a module or package (in this order)
        matching the name of the import, inside the nested directory of
        the module. Please take consideration of that
        the name must be simple, without dots. Returns the module or package
        or None if not found"""
        container = self
        #if the package holds __init__, the import is translated
        #to this file
        f = lambda x: x != self and x.inner_package == container
        m = dict([(x._name, x) for x in self(model.py.Module, filter=f, cut=True)])
        if '__init__' in m:
            return m['__init__']
        if name in m:
            return m[name]
        f = lambda x: x.parent.inner_package == container
        for x in self(model.py.Package, filter=f, cut=True):
            if x._name == name:
                return x
        return None

    @property
    def inner_class(self):
        """Get the innermost class container"""
        return None

