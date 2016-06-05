# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
import model
import model.decorator as ctx
import app.resources as rc
import tran


class Folder(model.TComponent):
    """Implements a Folder representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    module_container = True
    namespace_container = True
    function_container = True
    variable_container = True
    member_container = True

    # visual methods
    @tran.TransactionalMethod('move folder {}')
    def drop(self, to):
        """Drops class inside project or another folder """
        target = to.inner_folder_container
        if not target or self.inner_class != target.inner_class or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        super(Folder, self).__init__(**kwargs)
        self.update_container()

    def update_container(self):
        """Update the container info"""
        self.class_container = self._parent.class_container
        self.context_container = self._parent.context_container
        self.folder_container = self._parent.folder_container
        self.diagram_container = self._parent.diagram_container
        self.module_container = self._parent.module_container
        self.namespace_container = self._parent.namespace_container
        self.function_container = self._parent.function_container
        self.variable_container = self._parent.variable_container
        self.member_container = self._parent.member_container
        self.import_container = self._parent.import_container

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Folder, self).get_kwargs()

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the folder declaration"""
        self.WriteComment(pf)
        #we will follow and respect the visual order
        child_types = [model.Folder, model.cc.Namespace,
            model.cc.Class, model.cc.Enum, model.cc.MemberData,
            model.cc.Constructor, model.cc.MemberMethod,
            model.cc.Destructor, model.cc.Module,
            model.cc.Function, model.cc.Data]
        for type in child_types:
            if len(self[type]):
                for item in self[type]:
                    item.WriteDeclaration(pf)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folder")

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folder_open")

    def ExistMemberDataNamed(self, name):
        """Check recursively about the existence of nested child member"""
        from MemberData import MemberData
        return self.hasChild(name=name, type=MemberData)

    def AddMemberData(self, name):
        """Add a member element"""
        from MemberData import MemberData
        member = MemberData(name, self)
        return member

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        if type(self.parent) not in [model.Folder, model.cc.Class]:
            return []
        return self.parent.nested_classes
