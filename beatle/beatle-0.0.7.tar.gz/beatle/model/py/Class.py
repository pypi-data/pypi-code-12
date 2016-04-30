# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""

import model
import os
import copy
from model.writer import writer
import app.resources as rc
import ctx
import tran
from app.utils import cached_type


class Class(model.TComponent):
    """Implements python class representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    inheritance_container = True
    member_container = True
    relation_container = True
    enum_container = False
    type_container = False
    import_container = True

    # visual methods
    @tran.TransactionalMethod('move python class {}')
    def drop(self, to):
        """Drops class inside project or another folder """
        target = to.inner_class_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._deriv = kwargs.get('derivatives', [])
        self._memberPrefix = kwargs.get('prefix', '_')
        self._export = kwargs.get('export', False)

        self._lastHdrTime = None
        self._lastSrcTime = None
        super(Class, self).__init__(**kwargs)
        # add object derivative
        if not kwargs.get('raw', False):
            if self._name != 'object':
                for cls in self.project.level_classes:
                    if cls._name == 'object':
                        model.py.Inheritance(parent=self,
                            ancestor=cls, note='standard inheritance')
                        break
        k = self.inner_module or self.inner_package
        if k:
            k.ExportPythonCodeFiles()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['derivatives'] = self._deriv
        kwargs['prefix'] = self._memberPrefix
        kwargs.update(super(Class, self).get_kwargs())
        return kwargs

    def lower(self):
        """Criteria for sorting when generating code"""
        return self._inheritance_level

    def GetClassArguments(self):
        """Get the list of arguments required by the class"""
        return []

    def UpdateClassRelations(self):
        """This method gets invoked when something changes in
        class relations specification
        and ensure mainteinance of internal methods and ctors"""
        pass

    def AutoInit(self):
        """Update all init ctors"""
        pass

    def UpdateInitCalls(self):
        """Update the calls to init method"""
        pass

    def UpdateExitCalls(self):
        """Update the calls to exit method"""
        pass

    def AutoArgs(self):
        """Update all ctor arguments"""
        pass

    def updateSources(self, force=False):
        """does source generation"""
        pass

    def GetPreferredConstructor(self):
        """Obtiene el constructor por defecto o None"""
        return None

    def GetSerialConstructor(self):
        """Obtiene el constructor de serializacion o None"""
        return None

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return True

    def Delete(self):
        """Delete diagram objects"""
        #new version
        for dia in self.project(model.ClassDiagram):
            # Check if inherit is in
            elem = dia.FindElement(self)
            if elem is not None:
                dia.SaveState()
                dia.RemoveElement(elem)
        k = self.inner_module or self.inner_package
        super(Class, self).Delete()
        if k:
            k.ExportPythonCodeFiles()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(Class, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(Class, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(Class, self).SaveState()

    def OnUndoRedoRemoving(self, root=True):
        """Prepare object to delete"""
        super(Class, self).OnUndoRedoRemoving(root)

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Class, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Class, self).OnUndoRedoAdd()

    def ExportPythonCode(self, wf):
        """Export python code"""
        from Inheritance import Inheritance
        wf.writenl()
        ins = ','.join([x._name for x in self[Inheritance]])
        if ins:
            ins = '(' + ins + ')'
        wf.openbrace('{self.label}{ins}:'.format(self=self, ins=ins))
        wf.writecomment(self._note)
        wf.writenl()

        #filters
        class_data = lambda x: x._scope == 'class' and x.inner_class == self

        #filter for instance members
        #instace_data = lambda x: x.self._scope == 'instance'

        #filter for skipping nested classes in methods
        same_class = lambda x: x.inner_class == self

        from Import import Import
        from MemberData import MemberData
        from InitMethod import InitMethod
        from MemberMethod import MemberMethod

        wf.writeln("#imports")
        for obj in self(Import, filter=same_class, cut=True):
            obj.ExportPythonCode(wf)
        wf.writenl()

        wf.writeln("#global data")
        for obj in self(MemberData, filter=class_data, cut=False):
            obj.ExportPythonCode(wf)
        wf.writenl()

        wf.writeln("#init method")
        for obj in self(InitMethod, filter=same_class, cut=True):
            obj.ExportPythonCode(wf)
        wf.writenl()

        wf.writeln("#member methods")
        for obj in self(MemberMethod, filter=same_class, cut=True):
            obj.ExportPythonCode(wf)
        wf.writenl()

        wf.closebrace()
        wf.writenl()

        return True

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('py_class')

    @property
    def label(self):
        """Get tree label"""
        return 'class {clase._name}'.format(clase=self)

    @property
    def path_name(self):
        """Get the full path"""
        if self.inner_module is not None:
            return '{self.inner_module.path_name}.{self._name}'.format(self=self)
        return self._name

    @property
    def file_container(self):
        """get the container filename (without extension)"""
        if self.inner_module:
            return self.inner_module._name
        if self.inner_package:
            return self.inner_package._name
        return self.project._name

    @property
    def context_name(self):
        """get the class name with path through parent classes"""
        pclass = self.parent.inner_class
        if pclass:
            return '{pclass.context_name}.{self._name}'.format(pclass=pclass, self=self)
        return self._name

    @property
    def tree_label(self):
        """Get tree label"""
        cos = 'class'
        return '{cos} {self.parent.scope}{self._name}'.format(cos=cos,
            self=self)

    def IsAncestor(self, cls):
        """Checks for ancestor relationship"""
        if cls is None:
            return False
        from model.py import Inheritance
        if not Inheritance in cls._child:
            return False
        inhmap = cls[Inheritance]
        for inh in inhmap:
            if inh._ancestor == self:
                return True
            if self.IsAncestor(inh._ancestor):
                return True
        return False

    def ExistMemberData(self, name):
        """Check recursively about the existence of nested child member"""
        # TO-DO
        return False

    def UpdateInitMethod(self):
        """Update the init methods"""
        # TO-DO
        pass

    def UpdateExitMethod(self):
        """update the exit methods"""
        # TO-DO
        pass

    @property
    def inner_class(self):
        """Get the inner class container"""
        return self

    @property
    def outer_class(self):
        """Get the outer class container"""
        return (self.parent and self.parent.outer_class) or self

    @property
    def is_class_methods(self):
        """returns the list of all is_class_methods"""
        # TO-DO
        return []

    @property
    def init_methods(self):
        """returns the setup relation method"""
        # TO-DO
        return []

    @property
    def exit_methods(self):
        """returns the clean relations method"""
        # TO-DO
        return []

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        if type(self.parent) not in [model.Folder, model.py.Class]:
            return [self]
        return self.parent.nested_classes + [self]

    @property
    def scope(self):
        """Get the scope"""
        return '{self.parent.scope}{self._name}.'.format(self=self)

    @property
    def inheritance(self):
        """Get the inheritance list"""
        # TO-DO
        return []


