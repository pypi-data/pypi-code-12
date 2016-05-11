# -*- coding: utf-8 -*-
import uuid
import app
from ctx import theContext as context
import model
import tran
#import tasks

"""
Created on Sun Dec 15 23:49:51 2013

@author: mel
"""


class TCommon(object):
    """Clase para componentes con soporte transamodelional"""
    task_container = False
    project_container = False
    class_container = False
    context_container = False
    folder_container = False
    diagram_container = False
    module_container = False
    namespace_container = False
    type_container = False
    inheritance_container = False
    member_container = False
    argument_container = False
    relation_container = False
    function_container = False
    variable_container = False
    enum_container = False
    import_container = False
    package_container = False
    library_container = False
    repository_container = False
    dir_container = False
    file_container = False

    #visual methods
    def draggable(self):
        """returns info about if the object can be moved"""
        return not self._readOnly

    def drop(self, to):
        """drop this elemento to another place"""
        return False

    def __init__(self, **kwargs):
        """Initialize a transactional component"""
        self._parent = kwargs.get('parent', None)
        self._name = kwargs.get('name', '')
        self._serial = kwargs.get('serial', False)
        self._note = kwargs.get('note', '')
        self._readOnly = kwargs.get('readonly', False)
        self._visibleInTree = kwargs.get('visibleInTree', True)
        self._declare = kwargs.get('declare', True)
        self._implement = kwargs.get('implement', True)
        self._child = {}
        if self._parent is not None:
            self._parent.addChild(self, kwargs.get('prev', None))
        self._uid = uuid.uuid4()
        super(TCommon, self).__init__(**kwargs)

        # allow to dynamic children creation through kwargs
        child_kwargs = kwargs.get('child_kwargs', None)
        if child_kwargs is not None:
            for t in child_kwargs:
                for chkwargs in child_kwargs[t]:
                    chkwargs['parent'] = self
                    t(**chkwargs)

    @property
    def uid(self):
        """Accessor to the uid of the object"""
        return self._uid

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['parent'] = self._parent
        kwargs['name'] = self._name
        kwargs['serial'] = self._serial
        kwargs['note'] = self._note
        kwargs['readonly'] = self._readOnly
        kwargs['visibleInTree'] = self._visibleInTree
        kwargs['declare'] = self._declare
        kwargs['implement'] = self._implement
        # recursively add child kwargs
        kwargs['child_kwargs'] = dict([(t,
            [x.get_kwargs() for x in self._child[t]]) for t in self._child.keys()])
        return kwargs

    def update_container(self):
        """Update the container info"""
        pass

    def WriteComment(self, pf):
        """Write the note using the writter"""
        #ok, now we place comments, if any
        if len(self._note) > 0:
            pf.writeln("/**")
            txt = self._note
            txt.replace('\r', '')
            lines = txt.split("\n")
            for line in lines:
                line.replace('*/', '* /')
                pf.writeln("* {}".format(line))
            pf.writeln("**/")

    def WriteContextsPrefixDeclaration(self, pf):
        """Write the contexts prefixes for declaration"""
        if hasattr(self, '_contexts'):
            for i in range(0, len(self._contexts)):
                item = self._contexts[i]
                if len(item._prefix_declaration):
                    pf.writeln('{}'.format(item._prefix_declaration))

    def WriteContextsSufixDeclaration(self, pf):
        """Write the contexts sufixes for declaration"""
        if hasattr(self, '_contexts'):
            for i in range(len(self._contexts) - 1, -1, -1):
                item = self._contexts[i]
                if len(item._sufix_declaration):
                    pf.writeln('{}'.format(item._sufix_declaration))

    def WriteContextsPrefixImplementation(self, pf):
        """Write the contexts prefixes for implementation"""
        if hasattr(self, '_contexts'):
            for i in range(0, len(self._contexts)):
                item = self._contexts[i]
                if len(item._prefix_implementation):
                    pf.writeln('{}'.format(item._prefix_implementation))

    def WriteContextsSufixImplementation(self, pf):
        """Write the contexts sufixes for implementation"""
        if hasattr(self, '_contexts'):
            for i in range(len(self._contexts) - 1, -1, -1):
                item = self._contexts[i]
                if len(item._sufix_implementation):
                    pf.writeln('{}'.format(item._sufix_implementation))

    def __call__(self, *args, **kwargs):
        """___call__(type1,...,typeN, filter=lambda x: True, cut=False):
        Returns the list of nested childs of one of the types.

        filter: indicates a boolean filter method that must
                return True for valid elements.

        cut: stops traveling if filter is unsatisfied?
        """
        r = []
        fn = kwargs.get('filter', lambda x: True)
        cut = kwargs.get('cut', False)
        for k in self._child:
            if app.isclass(k, *args):
                r.extend(filter(fn, self[k]))
            if cut:
                for o in filter(fn, self[k]):
                    r.extend(o(*args, **kwargs))
            else:
                for o in self[k]:
                    r.extend(o(*args, **kwargs))
        return r

    @property
    def name(self):
        """Get the name"""
        return self._name

    @property
    def note(self):
        """Get the name"""
        return self._note

    @note.setter
    def note(self, note):
        """Set the note"""
        self._note = note

    @property
    def label(self):
        """Get tree label"""
        return self._name

    @property
    def tree_label(self):
        """Get tree label"""
        return self.label

    @property
    def tab_label(self):
        """Get tree label"""
        return self.label

    #container properties
    @property
    def inner_class_container(self):
        """return the inner class container if any"""
        return (self.class_container and self) or (self.parent and self.parent.inner_class_container)

    @property
    def inner_context_container(self):
        """return the inner context container if any"""
        return (self.context_container and self) or (self.parent and self.parent.inner_context_container)

    @property
    def inner_folder_container(self):
        """return the inner folder container if any"""
        return (self.folder_container and self) or (self.parent and self.parent.inner_folder_container)

    @property
    def inner_repository_container(self):
        """return the inner folder container if any"""
        return (self.repository_container and self) or (self.parent and self.parent.inner_repository_container)

    @property
    def inner_diagram_container(self):
        """return the inner diagram container if any"""
        return (self.diagram_container and self) or (self.parent and self.parent.inner_diagram_container)

    @property
    def inner_module_container(self):
        """return the inner module container if any"""
        return (self.module_container and self) or (self.parent and self.parent.inner_module_container)

    @property
    def inner_task_container(self):
        """return the inner task container if any"""
        return (self.task_container and self) or (self.parent and self.parent.inner_task_container)

    @property
    def inner_type_container(self):
        """return the inner module container if any"""
        return (self.type_container and self) or (self.parent and self.parent.inner_type_container)

    @property
    def inner_enum_container(self):
        """return the inner module container if any"""
        return (self.enum_container and self) or (self.parent and self.parent.inner_enum_container)

    @property
    def inner_namespace_container(self):
        """return the inner namespace container if any"""
        return (self.namespace_container and self) or (self.parent and self.parent.inner_namespace_container)

    @property
    def inner_inheritance_container(self):
        """return the inner ineritance container if any"""
        return (self.inheritance_container and self) or (self.parent and self.parent.inner_inheritance_container)

    @property
    def inner_member_container(self):
        """return the inner member container"""
        return (self.member_container and self) or (self.parent and self.parent.inner_member_container)

    @property
    def inner_argument_container(self):
        """return the inner argument container"""
        return (self.argument_container and self) or (self.parent and self.parent.inner_argument_container)

    @property
    def inner_package_container(self):
        """return the inner package container"""
        return (self.package_container and self) or (self.parent and self.parent.inner_package_container)

    @property
    def inner_project_container(self):
        """return the inner project container"""
        return (self.project_container and self) or (
            self.parent and self.parent.inner_project_container)

    @property
    def inner_relation_container(self):
        """return the inner relation container"""
        return (self.relation_container and self) or (
            self.parent and self.parent.inner_relation_container)

    @property
    def inner_function_container(self):
        """return the inner function container"""
        return (self.function_container and self) or (self.parent and self.parent.inner_function_container)

    @property
    def inner_variable_container(self):
        """return the inner relation container"""
        return (self.variable_container and self) or (self.parent and self.parent.inner_variable_container)

    @property
    def inner_import_container(self):
        """return the inner relation container"""
        return (self.import_container and self) or (self.parent and self.parent.inner_import_container)

    def inner(self, t, self_include=True):
        """Search through ancestors the first ancestor of some type"""
        if self_include:
            if (type(t) is list and app.isclass(type(self), *t)) or app.isclass(type(self), t):
                return self
        return self._parent and self._parent.inner(t)

    @property
    def can_delete(self):
        """Check about if a component can be deleted"""
        return not self._readOnly

    @property
    def read_only(self):
        """get read only status"""
        return self._readOnly

    def __setitem__(self, cls, listobj):
        """sets the list of some class childs"""
        assert type(listobj) is list
        self._child[cls] = listobj

    def __getitem__(self, cls):
        """returns the list of childs with some class"""
        if not cls in self._child:
            self._child[cls] = []
        return self._child[cls]

    @property
    def project(self):
        """return the container project"""
        return self.inner(model.Project)

    @property
    def workspace(self):
        """return the container project"""
        return self.inner(model.Workspace)

    @property
    def inner_types_folder(self):
        """return the container types folder"""
        return self.inner(model.cc.TypesFolder)

    @property
    def classes(self):
        """returns the list of all classes"""
        return self(model.cc.Class)

    @property
    def diagrams(self):
        """returns the list of all diagrams"""
        return self(model.ClassDiagram)

    @property
    def namespaces(self):
        """returns the list of all namespaces"""
        return self(model.cc.Namespace)

    @property
    def folders(self):
        """returns the list of all folder"""
        return self(model.Folder)

    @property
    def modules(self):
        """returns the list of all modules"""
        return self(model.cc.Module, model.py.Module)

    @property
    def packages(self):
        """returns the list of all packages"""
        return self(model.py.Package)

    @property
    def functions(self):
        """returns the list of all functions"""
        return self(model.cc.Function)

    @property
    def constructors(self):
        """returns the list of all functions"""
        return self(model.cc.Constructor)

    @property
    def destructors(self):
        """returns the list of all functions"""
        return self(model.cc.Destructor)

    @property
    def methods(self):
        """returns the list of all functions"""
        return self(model.cc.MemberMethod)

    @property
    def variables(self):
        """returns the list of all variables"""
        return self(model.cc.Data, True)

    @property
    def inner_class(self):
        """returns the innermost class"""
        return self.parent and self.parent.inner_class

    @property
    def inner_namespace(self):
        """returns the innermost class"""
        return self.inner(model.cc.Namespace)

    @property
    def inner_library(self):
        """returns the inner library if any"""
        return self.inner(model.Library)

    @property
    def inner_folder(self):
        """returns the innermost folder"""
        return self.inner(model.Folder)

    @property
    def inner_module(self):
        """returns the innermost class"""
        return self.inner([model.cc.Module, model.py.Module])

    @property
    def inner_package(self):
        """returns the innermost class"""
        return self.inner(model.py.Package)

    @property
    def inner_method(self):
        """returns the innermost folder"""
        return self.inner([model.cc.MemberMethod, model.cc.IsClassMethod])

    @property
    def inner_function(self):
        """returns the innermost folder"""
        return self.inner(model.cc.Function)

    @property
    def inner_constructor(self):
        """returns the innermost folder"""
        return self.inner(model.cc.Constructor)

    @property
    def outer_class(self):
        """returns the outermost class"""
        return self.parent and self.parent.outer_class

    @property
    def outer_module(self):
        """returns the outermost module"""
        return (self.parent and self.parent.outer_module) or ((
            isinstance(self, (model.cc.Module, model.py.Module)) or None) and self)

    @property
    def outer_namespace(self):
        """returns the outermost namespace"""
        return (self.parent and self.parent.outer_namespace) or ((
            isinstance(self, model.cc.Namespace) or None) and self)

    @property
    def outer_folder(self):
        """returns the outermost folder"""
        return (self.parent and self.parent.outer_folder) or ((
            isinstance(self, model.Folder) or None) and self)

    @property
    def types(self):
        """This method gets the list of visible types"""
        return (self.outer_class or self.parent).types

    @property
    def level_classes(self):
        """return the list of classes inside this level"""
        cls = self.outer_class
        return self(model.cc.Class, model.py.Class, filter=lambda x: x.parent.outer_class == cls)

    @property
    def top_namespaces(self):
        """return the list of top namespaces"""
        return [x for x in self.namespaces if x.outer_namespace == x]

    @property
    def top_folders(self):
        """return the list of top folders"""
        return [x for x in self.folders if x.outer_folder == x]

    @property
    def parent(self):
        """return the parent object"""
        return self._parent

    @property
    def path(self):
        """returns the ordered parents list"""
        return ((self.parent and self.parent.path) or []) + [self]

    @property
    def scope(self):
        """Get the scope"""
        return (self._parent and self._parent.scope) or ''

    @property
    def scoped_name(self):
        """returns the absolute name, with scope"""
        return '{self.scope}{self._name}'.format(self=self)

    @property
    def template_types(self):
        """Returns the list of nested template types"""
        return (self.parent and self.parent.template_types) or []

    def addChild(self, obj, prev=None):
        """Adds a child member to dictionary"""
        cls = type(obj)
        if cls not in self._child:
            self._child[cls] = [obj]
        elif obj not in self._child[cls]:
            ls = self._child[cls]
            if prev is not None:
                if prev in ls:
                    ls.insert(ls.index(prev) + 1, obj)
                else:
                    ls.insert(0, obj)
            else:
                ls.append(obj)

    def removeChild(self, obj):
        """Remove a child member from dictionary"""
        cls = type(obj)
        if cls in self._child and obj in self._child[cls]:
            self._child[cls].remove(obj)

    def hasChild(self, **kwargs):
        """Checks the existence of some child"""
        recurse = kwargs.get('recurse', True)
        obj = kwargs.get('obj', None)
        if obj is not None:
            t = type(obj)
            if not recurse:
                return obj in self[t]
        else:
            t = kwargs.get('type', None)
            name = kwargs.get('name', None)
            if not recurse:
                return name in [x._name for x in self[t]]
        for c, l in [(u, v) for u, v in self._child.items()
            if hasattr(u, 'hasChild')]:
            for x in l:
                if x.hasChild(**kwargs):
                    return True
        return False

    def __getstate__(self):
        """Set picke context"""
        state = dict(self.__dict__)
        if '_parentIndex' in state:
            del state['_parentIndex']
        if '_pane' in state:
            del state['_pane']
        if '_paneIndex' in state:
            del state['_paneIndex']
        return state

    def Delete(self):
        """Remove all the elements"""
        self.DeleteChilds()
        super(TCommon, self).Delete()

    def DeleteChilds(self):
        """Remove all the child elements"""
        items = self._child.keys()
        for cl in items:
            rm = [x for x in self._child[cl]]
            for x in rm:
                x.Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        if self._parent is not None:
            self._parent.removeChild(self)

    def RestoreRelations(self):
        """Utility for undo/redo"""
        if self._parent is not None:
            self._parent.addChild(self)

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(TCommon, self).OnUndoRedoChanged()
        self.update_container()
        context.RenderUndoRedoChanged(self)

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        super(TCommon, self).OnUndoRedoRemoving()
        for cl, ls in self._child.items():
            for x in ls:
                x.OnUndoRedoRemoving(False)
        if root and self.parent is not None:
            l = self.parent[type(self)]
            if self in l:
                self._parentIndex = l.index(self)
                l.pop(self._parentIndex)
        context.RenderUndoRedoRemoving(self)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        # Our first step is check if element was created first and must
        # be repositioned in concrete place of his parent.
        super(TCommon, self).OnUndoRedoAdd()
        if self._parent is not None and hasattr(self, '_parentIndex'):
            l = self._parent[type(self)]
            if self in l:
                l.remove(self)
            l.insert(self._parentIndex, self)
            delattr(self, '_parentIndex')
        # We can have a context rendering
        context.RenderUndoRedoAdd(self)
        rlc = list(reversed(list(self._child.keys())))
        for c in rlc:
            rlo = list(reversed(self._child[c]))
            for o in rlo:
                o.OnUndoRedoAdd()

    def OnUndoRedoLoaded(self):
        """Restore object after loading"""
        context.RenderLoadedAdd(self)
        rlc = list(reversed(list(self._child.keys())))
        for c in rlc:
            rlo = list(reversed(self._child[c]))
            for o in rlo:
                o.OnUndoRedoLoaded()

    def OnUndoRedoUnloaded(self):
        """Restore object after loading"""
        rlc = list(reversed(list(self._child.keys())))
        for c in rlc:
            rlo = list(reversed(self._child[c]))
            for o in rlo:
                o.OnUndoRedoUnloaded()
        context.RenderUndoRedoRemoving(self)

