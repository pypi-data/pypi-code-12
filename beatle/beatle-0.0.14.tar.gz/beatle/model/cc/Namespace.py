# -*- coding: utf-8 -*-
"""
Created on Fri July 3 20:50:32 2015

@author: mel
"""
import model
import model.decorator as ctx
import tran
from app import resources
from tran import TransactionStack


class Namespace(model.TComponent):
    """Implements class representation"""

    class_container = True
    folder_container = True
    diagram_container = True
    module_container = True
    namespace_container = True
    function_container = True
    variable_container = True

    #visual methods
    @tran.TransactionalMethod('move namespace {}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_namespace_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0  # trick for insert as first child
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._lastSrcTime = None
        self._lastHdrTime = None
        super(Namespace, self).__init__(**kwargs)
        self.update_container()
        k = self.outer_class or self.outer_module or self.project
        if k:
            k.ExportCppCodeFiles(force=True)

    def Delete(self):
        """Handle delete"""
        k = self.outer_class or self.outer_module or self.project
        super(Namespace, self).Delete()
        if k:
            k.ExportCppCodeFiles(force=True)


    def update_container(self):
        """Update the container info"""
        if self.inner_module:
            self.class_container = False
            self.module_container = False
            self.function_container = True
            self.variable_container = True
        else:
            self.class_container = True
            self.module_container = True
            self.function_container = False
            self.variable_container = False

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(Namespace, self).get_kwargs())
        return kwargs

    def lower(self):
        """Criteria for sorting when generating code"""
        return self._inheritance_level

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the folder declaration"""
        #we will follow and respect the visual order
        self.WriteComment(pf)
        child_types = [model.Folder, model.cc.Namespace,
            model.cc.Class, model.cc.Enum, model.cc.MemberData,
            model.cc.Constructor, model.cc.MemberMethod,
            model.cc.Destructor, model.cc.Module,
            model.cc.Function, model.cc.Data]
        pf.openbrace('namespace {self._name}'.format(self=self))
        for type in child_types:
            if len(self[type]):
                for item in self[type]:
                    item.WriteDeclaration(pf)
        pf.closebrace(';')

    @property
    def can_delete(self):
        """Chack bout if this object may be deleted"""
        return super(Namespace, self).can_delete

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(Namespace, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(Namespace, self).RestoreRelations()

    def OnUndoRedoRemoving(self, root=True):
        """Prepare object to delete"""
        super(Namespace, self).OnUndoRedoRemoving(root)

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(Namespace, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            k = self.outer_class or self.outer_module
            if k:
                k.ExportCppCodeFiles(force=True)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Namespace, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return resources.GetBitmapIndex('namespace')

    @property
    def tree_label(self):
        """Get tree label"""
        return 'namespace {namespace._name}'.format(namespace=self)

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        if type(self.parent) in [model.Folder, model.cc.Class, model.Namespace]:
            return self.parent.nested_classes
        return []

    @property
    def scoped(self):
        """Get the scope"""
        return '{self.parent.scope}{self._name}'.format(self=self)

    @property
    def scope(self):
        """Get the scope"""
        return '{scoped}::'.format(scoped=self.scoped)
