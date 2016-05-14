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
import model.decorator as ctx
import tran
from tran import TransactionStack
from app.utils import cached_type


class Class(model.TComponent):
    """Implements c++ class representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    inheritance_container = True
    member_container = True
    relation_container = True
    enum_container = True
    type_container = True

    #default empty user sections
    user_code_h1 = ''
    user_code_h2 = ''
    user_code_h3 = ''
    user_code_s1 = ''
    user_code_s2 = ''
    user_code_s3 = ''

    # visual methods
    @tran.TransactionalMethod('move class {}')
    def drop(self, to):
        """Drops class inside project or another folder """
        target = to.inner_namespace_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._is_external = kwargs.get("is_external", False)
        self._is_struct = kwargs.get("is_struct", False)
        self._access = kwargs.get('access', "public")
        self._template = kwargs.get('template', None)
        self._template_types = kwargs.get('template_types', [])
        self._deriv = kwargs.get('derivatives', [])
        self._memberPrefix = kwargs.get('prefix', '_')
        self._lastHdrTime = None
        self._lastSrcTime = None
        self._header_obj = None  # vincle with file
        self._source_obj = None  # vincle with file
        super(Class, self).__init__(**kwargs)
        self.project.ExportCppCodeFiles(force=True)

    def set_source(self, source_obj):
        """Sets a vincle with a file"""
        self._source_obj = source_obj

    def set_header(self, header_obj):
        """Sets a vincle with a file"""
        self._header_obj = header_obj

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['is_struct'] = self._is_struct
        kwargs['access'] = self._access
        kwargs['template'] = self._template
        kwargs['template_types'] = self._template_types
        kwargs['derivatives'] = self._deriv
        kwargs['prefix'] = self._memberPrefix
        kwargs['is_external'] = self.is_external
        kwargs.update(super(Class, self).get_kwargs())
        return kwargs

    def lower(self):
        """Criteria for sorting when generating code"""
        return self._inheritance_level

    #backward compatibility code - to simplfy in newer versions
    @property
    def is_external(self):
        """return info about if the class is external"""
        if not hasattr(self, '_is_external'):
            self._is_external = False
        return self._is_external

    @property
    def virtual_bases(self):
        """Get the list of all virtual base classes"""
        # some comments: The inheritance icons will NEVER be hidden
        # by nested folders. It will be ALLWAYS be a direct child of class
        r = []
        for u in self[model.cc.Inheritance]:
            r.extend([x for x in u.virtual_bases if x not in r])
        return r

    def GetClassArguments(self):
        """Get the list of arguments required by the class"""
        # The arguments required by the class are determined following
        # the rules (in this order):
        # 1º Required arguments from virtual base classes
        # 2º Required arguments from normal base classes (not virtual)
        # 3º non-static Members without initialization
        # ** NOT: 4º Required arguments from relation parents...
        #
        # For base classes (both virtual or not), the required arguments
        # are either determined by preferred constructors, either none.
        #
        # Ok, let's go...
        # 1º & 2º.....
        vinh = self.virtual_bases
        ninh = [x._ancestor for x in self[model.cc.Inheritance] if x._ancestor not in vinh]
        # create a contributor's list
        inh = vinh
        inh.extend(ninh)
        arglist = []
        # append arguments from preferred ctors
        for x in inh:
            ctor = x.GetPreferredConstructor()
            if ctor is not None:
                for arg in ctor[model.cc.Argument]:
                    arglist.append(arg)
        # 3º append (without class prefix) non-static uninitialized members
        arglist.extend([x for x in
            self(model.cc.MemberData)
            if x.inner_class is self and x._static is False
            and len(x._default) == 0])
        # 4º append relations is not required: It must be constructed
        # from members
        # All is complete: Please note that the return list contains
        # arguments and data members, with possible duplcated types and
        # names, that require to be processed when generating the
        # initialization of constructors
        return arglist

    def UpdateClassRelations(self):
        """This method gets invoked when something changes in class relations specification
        and ensure mainteinance of internal methods and ctors"""
        self.UpdateInitMethod()
        self.UpdateExitMethod()
        self.AutoArgs()
        self.AutoInit()
        self.UpdateInitCalls()
        self.UpdateExitCalls()

    def AutoInit(self):
        """Update all init ctors"""
        for x in self(model.cc.Constructor,
            filter=lambda x: x.inner_class == self, cut=True):
            x.AutoInit()

    def UpdateInitCalls(self):
        """Update the calls to init method"""
        for x in self(model.cc.Constructor,
            filter=lambda x: x.inner_class == self, cut=True):
            x.UpdateInitCall()

    def UpdateExitCalls(self):
        """Update the calls to exit method"""
        for x in self(model.cc.Destructor, filter=lambda x: x.inner_class == self, cut=True):
            x.UpdateExitCall()

    def AutoArgs(self):
        """Update all ctor arguments"""
        for x in self(model.cc.Constructor,
            filter=lambda x: x.inner_class == self, cut=True):
            x.AutoArgs()

    def errorCheckDerivatives(self):
        """We have detected that deleted derivatives remains in
        some class object, so this method checks and warns"""
        errors = False
        n = []
        print "start check\n"
        if not hasattr(self, '_memberPrefix'):
            self._memberPrefix = '_'
        if not hasattr(self, '_is_struct'):
            self._is_struct = False
        if self._is_struct:
            cos = 'struct'
        else:
            cos = 'class'
        for cls in self._deriv:
            test = [u for u in cls[model.cc.Inheritance] if u._ancestor == self]
            if len(test) == 0:
                print "Dead inheritante from {} to {} {}\n".format(
                    self._name, cos, cls._name)
                errors = True
            else:
                n.append(cls)
        self._deriv = n
        return errors

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        stack = tran.TransactionStack
        method = self.ExportCppCodeFiles.inner
        if method not in stack.delayedCallsFiltered:
            stack.delayedCallsFiltered.append(method)
        super(Class, self).OnUndoRedoRemoving()

    @tran.DelayedMethod
    def ExportCppCodeFiles(self, force=False):
        """Do code generation"""
        self.updateSources(force)
        self.updateHeaders(force)

    @property
    def abs_path_source(self):
        """Return the absolute path of source"""
        return os.path.join(self.project.sources_dir, self._name + ".cpp")

    def updateSources(self, force=False):
        """does source generation"""
        fname = self.abs_path_source
        regenerate = False
        if force or not os.path.exists(fname) or self._lastSrcTime is None:
            regenerate = True
        elif os.path.getmtime(fname) < self._lastSrcTime:
            regenerate = True
        if not regenerate:
            return
        f = open(fname, 'w')
        pf = writer.for_file(f)
        #master include file
        prj = self.project

        pf.writeln("// {user.before.include.begin}")
        pf.writeln(self.user_code_s1)
        pf.writeln("// {user.before.include.end}")
        pf.writenl()
        if prj._useMaster:
            pf.writeln('#include "{}"'.format(prj._masterInclude))
        else:
            pf.writeln('#include "{}.h"'.format(self._name))
        pf.writenl()

        # some facility
        pf.writeln("#include <assert.h>")
        pf.writenl()

        self.WriteCode(pf)
        pf.writenl()
        f.close()

    @property
    def kind(self):
        """Returns the class flavor"""
        return (self._is_struct and "struct") or "class"

    def _ensure_access(self, pf, access):
        "utility method that ensures access update when needed"
        if access != self.contextAccess:
            self.contextAccess = access
            pf.writeln("{}:".format(access))

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the class declaration"""

        #if this is a nested class, ensure access
        pc = self.parent.inner_class
        if pc:
            pc._ensure_access(pf, self._access)

        cos = '{self.kind} {self._name}'.format(self=self)
        self.contextAccess = (self._is_struct and "public") or "private"
        self._inlines = []
        #ok, create user section
        pf.writeln("// {{user.before.{}.begin}}".format(cos))
        pf.writeln(self.user_code_h1)
        pf.writeln("// {{user.before.{}.end}}".format(cos))
        pf.writenl()

        self.WriteComment(pf)

        #create inheritance strings
        #from Inheritance import Inheritance
        if len(self[model.cc.Inheritance]):
            s = ": "
            for o in self[model.cc.Inheritance]:
                if o._virtual:
                    s += "{} virtual {},".format(o._access, o._name)
                else:
                    s += "{} {},".format(o._access, o._name)
            s = s[:-1]
        else:
            s = ""
        pf.writeln("{0} {1}{2}".format(self.kind, self._name, s))
        pf.openbrace()
        pf.writenl()
        pf.writeln("// {{user.inside.{}.begin}}".format(cos))
        pf.writeln(self.user_code_h2)
        pf.writeln("// {{user.inside.{}.end}}".format(cos))
        pf.writenl()

        #write friend declarations
        for f in self.friends:
            pf.writeln('friend {}'.format(f._target.declare))

        #write types
        _type = {'public': [], 'protected': [], 'private': []}
        f = lambda x: x.inner_class == self and getattr(x, '_definition', 'True').strip()
        for t in self(model.cc.Type, filter=f, cut=True):
            _type[t._access].append(t)
        for access in _type:
            if not _type[access]:
                continue
            pf.writeln('{}:'.format(access))
            pf.writenl()
            for t in _type[access]:
                pf.writeln('//type definition for {}'.format(t._name))
                pf.writeln('{}'.format(t._definition))
                pf.writenl()

        #we will follow and respect the visual order
        self_element = lambda x: x.parent.inner_class == self
        for element in self(model.cc.Enum, Class, model.cc.MemberData,
            model.cc.Constructor, model.cc.MemberMethod, model.cc.InitMethod,
             model.cc.ExitMethod, model.cc.IsClassMethod, model.cc.Destructor,
            filter=self_element, cut=True):
            element.WriteDeclaration(pf)

        pf.closebrace(";")
        pf.writenl()
        pf.writeln("// {{user.after.{}.begin}}".format(cos))
        pf.writeln(self.user_code_h3)
        pf.writeln("// {{user.after.{}.end}}".format(cos))
        pf.writenl()
        del self.contextAccess

    @property
    def abs_path_header(self):
        """Return the absolute path of source"""
        return os.path.join(self.project.headers_dir, self._name + ".h")

    def updateHeaders(self, force=False):
        """Realiza la generacion de fuentes"""
        fname = self.abs_path_header
        regenerate = False
        if force or not os.path.exists(fname) or self._lastHdrTime is None:
            regenerate = True
        elif os.path.getmtime(fname) < self._lastHdrTime:
            regenerate = True
        if not regenerate:
            return
        f = open(fname, 'w')
        pf = writer.for_file(f)
        #create safeguard
        safeguard = self._name.upper() + "_H_INCLUDED"
        pf.writeln("#if !defined({})".format(safeguard))
        pf.writeln("#define {}".format(safeguard))
        pf.writenl()

        #we are using master include? if not, include inheritances
        p = self.project
        if not p._useMaster and self.outer_class == self:
            #iterate over inheritances
            if len(self._child[model.cc.Inheritance]):
                pf.writeln("//base includes")
                for o in self[model.cc.Inheritance]:
                    pf.writeln("#include \"{}.h\"".format(o._name))
                pf.writenl()
            #we need to forward references for relations
            if len(self.child[model.cc.RelationFrom]):
                pf.writeln("//forward references of parent classes")
                for p in self[model.cc.RelationFrom]:
                    pf.writeln(p._FROM.reference)
            if len(self.child[model.cc.RelationTo]):
                pf.writeln("//forward references of child classes")
                for p in self[model.cc.RelationFrom]:
                    pf.writeln(p._TO.reference)
        pf.writenl()
        self.WriteDeclaration(pf)
        #end safeguard
        pf.writeln("#endif //{0}".format(safeguard))
        #write inlines
        pf.writenl()
        if len(self._inlines) > 0:
            pf.writeln("#if defined(INCLUDE_INLINES)")
            pf.writeln("#if !defined(INCLUDE_INLINES_{name})".format(name=self._name.upper()))
            pf.writeln("#define INCLUDE_INLINES_{name}".format(name=self._name.upper()))
            pf.writenl()
            for o in self._inlines:
                o.WriteCode(pf)
                pf.writenl()
            pf.writeln("#endif //(INCLUDE_INLINES_{name})".format(name=self._name.upper()))
            pf.writeln("#endif //INCLUDE_INLINES")
            pf.writenl()
        del self._inlines
        self._lastHdrTime = os.path.getmtime(fname)
        pf.writenl()
        f.close()

    @ctx.ContextImplementation()
    def WriteCode(self, pf):
        """Write code for class"""
        tag = '{self.kind}.{self._name}'.format(self=self)
        pf.writeln("// {{user.before.{tag}.begin}}".format(tag=tag))
        pf.writeln(self.user_code_s2)
        pf.writeln("// {{user.before.{tag}.end}}".format(tag=tag))
        pf.writenl()

        # we have an interesting problem here:
        # From the point of view of easy coding and track context
        #we will follow and respect the visual order
        self_member = lambda x: x.parent.inner_class == self and (not hasattr(x, '_inline') or not x._inline)
        if self.outer_class == self:
            elements = self(model.cc.MemberData, filter=lambda x: x._static)
        else:
            elements = []
        #do it with steps for ensuring order
        elements += self(model.cc.InitMethod, filter=self_member, cut=True)
        elements += self(model.cc.ExitMethod, filter=self_member, cut=True)
        elements += self(model.cc.Constructor, filter=self_member, cut=True)
        elements += self(model.cc.IsClassMethod, filter=self_member, cut=True)
        elements += self(model.cc.MemberMethod, filter=self_member, cut=True)
        elements += self(model.cc.Destructor, filter=self_member, cut=True)
        elements += self(Class, filter=self_member, cut=True)

        # obtain all the interesting elements and write
        for element in elements:
            element.WriteCode(pf)

        pf.writenl()
        pf.writeln("// {{user.after.{tag}.begin}}".format(tag=tag))
        pf.writeln(self.user_code_s3)
        pf.writeln("// {{user.after.{tag}.end}}".format(tag=tag))
        pf.writenl()

    def GetPreferredConstructor(self):
        """Obtiene el constructor por defecto o None"""
        ctors = self(model.cc.Constructor)
        for ctor in ctors:
            if ctor.IsPreferred():
                return ctor
        # if not preferred, we return the first if any
        if len(ctors):
            return ctors[0]
        return None

    def GetSerialConstructor(self):
        """Obtiene el constructor de serializacion o None"""
        for ctor in self(model.cc.Constructor):
            if ctor.IsSerial():
                return ctor
        return None

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        if len(self._deriv) > 0:
            return False
        project = self.project
        #Obtenemos la lista de miembros de clase
        if project is not None:
            #check if outer element is using this class
            outer = lambda x: self not in x.path
            typed = project(model.cc.MemberData, model.cc.MemberMethod,
                model.cc.Argument, filter=outer, cut=True)
            typed += project(model.cc.Function, model.cc.Data)
            for x in typed:
                if x._typei._type == self:
                    return False
        return super(Class, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        project = self.project
        for dia in self.project(model.ClassDiagram):
            # Check if inherit is in
            elem = dia.FindElement(self)
            if elem is not None:
                dia.SaveState()
                dia.RemoveElement(elem)
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        if hasattr(self, '_header_obj') and self._header_obj:
            self._header_obj.Delete()
        if hasattr(self, '_source_obj') and self._source_obj:
            self._source_obj.Delete()
        super(Class, self).Delete()
        project.ExportCppCodeFiles(force=True)

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(Class, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(Class, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        for rf in self[model.cc.RelationFrom]:
            rf._key.SaveState()
        for rt in self[model.cc.RelationTo]:
            rt._key.SaveState()
        super(Class, self).SaveState()

    def OnUndoRedoChanged(self):
        """Update from app"""
        #when the class is updated, ctor's and dtors, must be updated
        for ctor in self(model.cc.Constructor):
            ctor._name = self._name
            ctor.OnUndoRedoChanged()
        for dtor in self(model.cc.Destructor):
                dtor._name = self._name
                dtor.OnUndoRedoChanged()
        #inheritance labels must be changed
        for deriv in self._deriv:
            for inh in deriv[model.cc.Inheritance]:
                if inh._ancestor == self:
                    inh._name = self._name
                    inh.OnUndoRedoChanged()
        #relation labels must be changed?
        for rf in self[model.cc.RelationFrom]:
            rf._key._TO._name = "To" + self._name
            rf._key._TO.OnUndoRedoChanged()
        for rt in self[model.cc.RelationTo]:
            rt._key._FROM._name = "From" + self._name
            rt._key._FROM.OnUndoRedoChanged()
        project = self.project
        #update class diagrams
        dias = project(model.ClassDiagram)
        for dia in dias:
            # Check if class is in
            elem = dia.FindElement(self)
            if elem is not None:
                elem.Layout()
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        #update class usage as type
        typed = project(model.cc.MemberData, model.cc.MemberMethod, model.cc.Argument)
        subject = [x for x in typed if x._typei._type == self]
        # iteramos aplicando los cambios.
        for element in subject:
            element.OnUndoRedoChanged()
        super(Class, self).OnUndoRedoChanged()
        if not TransactionStack.InUndoRedo():
            project.ExportCppCodeFiles(force=True)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(Class, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        if not hasattr(self, '_access'):
            self._access = 'public'
        return rc.GetBitmapIndex('class', self._access)


    @property
    def tree_label(self):
        """Get tree label"""
        if self._is_struct:
            cos = 'struct'
        else:
            cos = 'class'
        if self._template:
            return 'template<{clase._template}> {cos} {clase._name}'.format(cos=cos, clase=self)
        else:
            return '{cos} {clase._name}'.format(cos=cos, clase=self)

    @property
    def declare(self):
        """"""
        if self._is_struct:
            cos = 'struct'
        else:
            cos = 'class'
        if self._template:
            return 'template<{clase._template}> {cos} {clase._name};'.format(cos=cos, clase=self)
        else:
            return '{cos} {clase._name};'.format(cos=cos, clase=self)

    def IsAncestor(self, cls):
        """Checks for ancestor relationship"""
        from model.cc import Inheritance
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
        from .MemberData import MemberData
        return self.hasChild(name=name, type=MemberData)

    def UpdateInitMethod(self):
        """Update the init methods"""
        method = self.init_methods
        aggregates = [x for x in self.relations_from if x._minCardinal]
        #if there are not relations we must delete init method
        if not aggregates:
            for x in method:
                x.Delete()
            return
        #ok, if there are not method we must create it and if
        #exists, unlist it
        if not method:
            method = model.cc.InitMethod(parent=self,
                type=model.cc.typeinst(type=cached_type(self.project, 'void')))
        else:
            method = method[0]
            method.SaveState()
            # remove all the arguments from the method
            k = method[model.cc.Argument]
            while k:
                k[0].Delete()
        #ok, we need to create a map for parent types
        code = ''
        for x in aggregates:
            cls = x._FROM
            #create required arguments
            name = x._fromPtr._name
            kwargs = {
                'parent': method,
                'name': name,
                'type': copy.copy(x._fromPtr._typei),
                'note': 'pointer to parent class {}'.format(cls._name)}
            model.cc.Argument(**kwargs)
            alias = x._key._TO._name
            code += '\t{name}->Add{alias}Last(this);\n'.format(
                name=name, alias=alias)
        method._content = code

    def UpdateExitMethod(self):
        """update the exit methods"""
        method = self.exit_methods
        parent_relations = self.relations_to
        child_relations = self.relations_from
        #if there are not relations we must delete init method
        if not parent_relations and not child_relations:
            for x in method:
                x.Delete()
            return
        #ok, if there are not method we must create it and if
        #exists, unlist it
        if not method:
            method = model.cc.ExitMethod(parent=self,
                type=model.cc.typeinst(type=cached_type(self.project, 'void')))
        else:
            method = method[0]
            method.SaveState()
        # computing the contents
        # for the aggregated relations, we must delete all the elements
        code = ''
        # first of all, remove the child part
        relations = []
        aggregated = []
        for x in child_relations:
            if x._minCardinal:
                aggregated.append(x)
            else:
                relations.append(x)
        for x in relations:
            name = x._fromPtr.prefixed_name
            alias = x._key._TO._name
            s = '\tif ( {name} != nullptr )\n'
            s += '\t{\n\t\t{name}->Remove{alias}(this);\n\t}\n'
            code += s.format(name=name, alias=alias)

        for x in aggregated:
            name = x._fromPtr.prefixed_name
            alias = x._key._TO._name
            s = '\t{name}->Remove{alias}(this);\n'
            code += s.format(name=name, alias=alias)

        relations = []
        aggregated = []

        for x in parent_relations:
            if x._key._FROM._minCardinal:
                aggregated.append(x)
            else:
                relations.append(x)
        # only agreggated may be releseaded first
        for x in relations:
            name = x._firstToPtr._name
            alias = x._name
            s = '\twhile ( {name} != nullptr )\n'
            s += '\t{\n\t\tRemove{alias}({name});\n\t}\n'
            code += s.format(name=name, alias=alias)
        #ok, we need to create a map for parent types
        for x in aggregated:
            alias = x._name
            code += '\tDeleteAll{alias}();\n'.format(alias=alias)
        method._content = code

    @property
    def inner_class(self):
        """Get the inner class container"""
        return self

    @property
    def outer_class(self):
        """Get the outer class container"""
        return (self.parent and self.parent.outer_class) or self

    @property
    def friends(self):
        """returns the list of all friends annotations inside this class"""
        member = lambda x: x.inner_class == self
        return self(model.cc.Friendship, filter=member, cut=True)

    @property
    def is_class_methods(self):
        """returns the list of all is_class_methods"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.IsClassMethod, filter=cls_member, cut=True)

    @property
    def init_methods(self):
        """returns the setup relation method"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.InitMethod, filter=cls_member, cut=True)

    @property
    def exit_methods(self):
        """returns the clean relations method"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.ExitMethod, filter=cls_member, cut=True)

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        if type(self.parent) not in [model.Folder, model.cc.Class]:
            return [self]
        return self.parent.nested_classes + [self]

    @property
    def nested_types(self):
        """return the visible nested types from here"""
        visible = lambda x: x.inner_class == self or getattr(x, '_access', 'public') == 'public'
        return self(model.cc.Type, Class, filter=visible, cut=True)

    @property
    def inherited_types(self):
        """return the visible types from base classes"""
        return list(set([t for x in self[model.cc.Inheritance] if x._access != 'private'
            for t in x._ancestor.nested_types]))

    @property
    def friend_types(self):
        """return the friend classes types"""
        friends = self.project(model.cc.Friendship, filter=lambda x: x._target == self)
        return list(set([t for x in friends for t in x.inner_class.nested_types]))

    @property
    def types(self):
        """This method gets the list of visible types"""
        return list(set(self.parent.types) | set(self.friend_types) |
            set(self.inherited_types) | set(self.nested_types))

    @property
    def template_types(self):
        """Returns the list of nested template types"""
        lt = self._template_types
        nt = super(Class, self).template_types
        lt.extend([x for x in nt if x not in self._template_types])
        return lt

    @property
    def scoped(self):
        """Get the scope"""
        if self._template:
            return '{self.parent.scope}{self._name}<{self._template}>'.format(self=self)
        return '{self.parent.scope}{self._name}'.format(self=self)

    def scoped_str(self, scope_list):
        """Gets the string representation with minimal relative scope"""
        s = self.scoped
        best_match = 0
        best_scope = None
        for x in scope_list:
            if s.find(x) == 0:
                if len(x) > best_match:
                    best_match = len(x)
                    best_scope = x
        if best_scope:
            s = s[best_match:]
            if s[:2] == '::':
                s = s[2:]
        return s

    @property
    def scope(self):
        """Get the scope"""
        return '{scoped}::'.format(scoped=self.scoped)

    @property
    def reference(self):
        """Gets the forward reference"""
        if self._template:
            return 'template<{self._template}> {self.kind} {self.scoped}'.format(self=self)
        return '{self.kind} {self.scoped}'.format(self=self)

    @property
    def relations_from(self):
        """Gets the relations from"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.RelationFrom, filter=cls_member, cut=True)

    @property
    def relations_to(self):
        """Gets the relations from"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.RelationTo, filter=cls_member, cut=True)

    @property
    def inheritance(self):
        """Get the inheritance list"""
        cls_member = lambda x: x.inner_class == self
        return self(model.cc.Inheritance, filter=cls_member, cut=True)



