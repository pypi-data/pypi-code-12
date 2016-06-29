# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
import model
import model.decorator as ctx
import app.resources as rc


class Library(model.TComponent):
    """Implements a Library representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    module_container = True
    namespace_container = True
    function_container = True
    variable_container = True
    member_container = False

    def __init__(self, **kwargs):
        """Initialization"""
        super(Library, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Library, self).get_kwargs()

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
        return rc.GetBitmapIndex("library")

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
