# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import os
import shutil
import time
import copy
import re
import wx
import model
import analytic
import app.resources as rc
from ctx import theContext as context
from model.writer import writer
import tran


class Project(model.TComponent):
    """Representation of C++ project"""

    folder_container = True
    diagram_container = True
    module_container = True

    def __init__(self, **kwargs):
        """Initialization of project"""
        self._dir = kwargs['dir']
        name = kwargs['name']
        self._language = kwargs.get('language', 'c++')
        self._includeDir = kwargs.get('includedir', "include")
        self._srcDir = kwargs.get('sourcedir', "src")
        self._useMaster = kwargs.get('usemaster', True)
        self._masterInclude = kwargs.get('masterinclude', name + ".h")
        self._author = kwargs.get('author', "<unknown>")
        self._date = kwargs.get('date', "08-10-2966")
        self._license = kwargs.get('license', None)
        self._type = kwargs.get('type', "unspecified")
        self._version = kwargs.get('version', [1, 0, 0])
        self._useMakefile = kwargs.get('usemakefile', False)
        self._types = kwargs.get('types', {})
        self._tasks = kwargs.get('tasks', [])
        self._contexts = kwargs.get('contexts', [])
        self._modified = True
        self._bookmarks = {}
        self._breakpoints = {}
        self._lastHdrTime = None
        super(Project, self).__init__(**kwargs)
        self.RegisterOutputDirs()
        if self._language == 'c++':
            import model.LibrariesFolder  # why I need this again?
            import model.cc  # why I need this again?
            self.namespace_container = True
            self.class_container = True
            self.package_container = False
            model.LibrariesFolder(parent=self, readonly=True)
            model.cc.TypesFolder(parent=self, readonly=True)
        else:
            import model.py  # why I need this again?
            self.namespace_container = False
            self.class_container = False
            self.package_container = True
            self.main_file = None
            self.py_file_pattern = re.compile('^(.)*.py$', re.I)
            # for python project, add hidden class object
            model.py.Class(parent=self, name='object',
                visibleInTree=False, declare=False, implement=False)
        #Add tasks control
        import model.tasks as tasks
        tasks.PendingTasks(parent=self)
        tasks.CurrentTasks(parent=self)
        tasks.FinishedTasks(parent=self)

    def breakpoints(self, model_file):
        """The breakpoints are stored using the uid of the object
        for reference"""
        uid = model_file.uid
        if uid not in self._breakpoints:
            self._breakpoints[uid] = {}
        return self._breakpoints[uid]

    def bookmarks(self, editable):
        """The bookmarks are stored using the uid of the object
        for reference. The editable objects may include ctors,
        dtors, standard methods or code files."""
        uid = editable.uid
        if uid not in self._bookmarks:
            self._bookmarks[uid] = {}
        return self._bookmarks[uid]

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['dir'] = self._dir
        kwargs['language'] = self._language
        kwargs['includedir'] = self._includedir
        kwargs['sourcedir'] = self._srcDir
        kwargs['usemaster'] = self._usemaster
        kwargs['masterinclude'] = self._masterinclude
        kwargs['author'] = self._author
        kwargs['date'] = self._date
        kwargs['license'] = self._license
        kwargs['type'] = self._type
        kwargs['version'] = self._version
        kwargs['usemakefile'] = self._useMakefile
        kwargs['types'] = self._types
        kwargs['tasks'] = self._tasks
        kwargs['contexts'] = copy.deepcopy(self._contexts)
        kwargs.update(super(Project, self).get_kwargs())
        return kwargs

    @property
    def types(self):
        """This method gets the list of visible types"""
        visible = lambda x: not x.inner_class or getattr(x, '_access', 'public') == 'public'
        return self(model.cc.Type, model.cc.Class, filter=visible, cut=True)

    def RegisterOutputDirs(self, logger=None):
        """Finds target generation directories and create it if missing."""
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
            if not os.path.exists(self._dir):
                e = "Project path missing: " + self._dir
                if logger is not None:
                    logger.AppendReportLine(e, wx.ICON_ERROR)
                wx.MessageBox(e, "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return False
        # for python projects, there are not other requiriments
        if self._language == 'python':
            return True
        sources_dir = os.path.join(self._dir, self._srcDir)
        headers_dir = os.path.join(self._dir, self._includeDir)
        sources_dir = os.path.realpath(sources_dir)
        headers_dir = os.path.realpath(headers_dir)
        if not os.path.exists(sources_dir):
            os.makedirs(sources_dir)
            if not os.path.exists(sources_dir):
                e = "Failed creating sources directory " + sources_dir
                if logger is not None:
                    logger.AppendReportLine(e, wx.ICON_ERROR)
                wx.MessageBox(e, "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return False
        if not os.path.exists(headers_dir):
            os.makedirs(headers_dir)
            if not os.path.exists(headers_dir):
                e = "Failed creating headers directory " + headers_dir
                if logger is not None:
                    logger.AppendReportLine(e, wx.ICON_ERROR)
                wx.MessageBox(e, "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return False
        self.sources_dir = sources_dir
        self.headers_dir = headers_dir
        return True

    def SortClasses(self):
        """Sort classes by inheritance level"""
        tc = [x for x in self.level_classes if not x.inner_library or x.inner_package]
        b = []
        index = 0
        while len(b) < len(tc):
            a = [x for x in tc if x not in b]
            for cls in a:
                for dcls in cls._deriv:
                    if dcls in a:
                        a.remove(dcls)
                # tambien consultamos las relaciones
                for toRel in cls(model.cc.RelationTo):
                    to = toRel._TO
                    if to in a:
                        a.remove(to)
            for cls in a:
                cls._inheritance_level = index
            b += a
            index = index + 1
        tc.sort(key=model.cc.Class.lower)
        for cls in tc:
            delattr(cls, '_inheritance_level')
        self.sorted_classes = tc

    def WriteTimestamp(self, pf, logger=None):
        """Write the timestamp and other info"""
        pf.writeln('/***')
        pf.writenl()
        pf.writeln(' File    :{}'.format(self._masterInclude))
        pf.writeln(' Created :{}'.format(time.strftime("%d/%m/%Y %H:%M:%S")))
        pf.writeln(' Author  :{}'.format(self._author))
        if self._license:
            pf.writenl()
            pf.writeln(' Licensed under {}'.format(self._license))
        pf.writenl()
        pf.writeln('***/')
        pf.writenl()

    def WriteForwards(self, pf, logger=None):
        """Write the forward class declarations"""
        pf.writeln('//forward references')
        for cls in self.sorted_classes:
            if cls.is_external:
                continue
            pf.writeln('{decl};'.format(decl=cls.reference))
        pf.writenl()

    def WriteMakefile(self, logger=None):
        """Write the makefile"""
        #open the file
        makefile = os.path.join(self._dir, 'Makefile')
        makefile = os.path.realpath(makefile)
        f = open(makefile, 'w')
        pf = writer.for_file(f)
        # write a very quick makefile
        # a ) definitions
        pf.writeln('# definitions')
        pf.writenl()
        pf.writeln('CC = g++')
        pf.writeln('AR = ar')
        pf.writeln('CFLAGS = -ggdb -fexceptions -Wall -std=c++0x -fPIC')
        pf.writeln('INCLUDE = -I{self._includeDir}'.format(self=self))
        pf.writeln('SRC = {self._srcDir}'.format(self=self))
        pf.writenl()
        # make targets all/clean
        # all : first, the prerequisites
        if self._type == "static library":
            product = self.name
        elif self._type == "dynamic library":
            product = '{name}.so'.format(name=self.name)
        elif self._type == "static library":
            product = 'lib{name}.a'.format(name=self.name)
        elif self._type == "executable":
            product = '{name}'.format(name=self.name)
        pf.writeln('all : {product}'.format(product=product))
        #master target
        pf.writenl()
        self.SortClasses()
        prerequisites = ' '.join(['{name}.o'.format(name=x.name) for x in self.sorted_classes if not x.is_external])
        pf.writeln('{product}: {prerequisites}'.format(product=product, prerequisites=prerequisites))
        if self._type == 'static library':
            pf.writeln('\t$(AR) -r -s ./{product} {prerequisites}'.format(
                product=product, prerequisites=prerequisites))
        elif self._type == 'dynamic library':
            pf.writeln('\t$(CC) -shared  {prerequisites}  -o {product}'.format(
                product=product, prerequisites=prerequisites))
        elif self._type == 'executable':
            pf.writeln('\t$(CC) {prerequisites}  -o {product}'.format(
                product=product, prerequisites=prerequisites))
        pf.writenl()
        # target files
        for cls in self.sorted_classes:
            if cls.is_external:
                continue
            pf.writeln('{name}.o: {src}/{name}.cpp {inc}/{name}.h'.format(name=cls.name,
                inc=self._includeDir, src=self._srcDir))
            pf.writeln('\t$(CC) $(CFLAGS) $(INCLUDE) -c {src}/{name}.cpp -o {name}.o'.format(src=self._srcDir,
                name=cls.name))
            pf.writenl()
        # clean
        pf.writeln('clean:')
        pf.writeln('\trm *.o {product}'.format(product=product))
        pf.writenl()
        f.close()

    def WriteMasterHeader(self, force=False, logger=None):
        """Write the master include file"""
        #open the file
        fname = os.path.join(self.headers_dir, self._masterInclude)
        regenerate = False
        if force or not os.path.exists(fname) or self._lastHdrTime is None:
            regenerate = True
        elif os.path.getmtime(fname) < self._lastHdrTime:
            regenerate = True
        if not regenerate:
            return True
        f = open(fname, 'w')
        pf = writer.for_file(f)

        #write a timestamp and version information
        self.WriteTimestamp(pf)

        safe_name = self._name.upper().replace('.','_')

        #write include safeward
        pf.writeln('#if !defined({name}_H_INCLUDED)'.format(name=safe_name))
        pf.writeln('#define {name}_H_INCLUDED'.format(name=safe_name))
        pf.writenl()

        #write the custom definitions
        if len(self._contexts) > 0:
            for item in self._contexts:
                if item._enable and len(item._define):
                    pf.writeln('/**')
                    pf.writeln('context {name}:'.format(name=item._name))
                    pf.writeln('{note}'.format(note=item.note))
                    pf.writeln('**/')
                    pf.writenl()
                    pf.writeln('{}'.format(item._define))
                    pf.writenl()

        #write custom types
        for t in self(model.cc.Type, filter=lambda x: type(x.parent) is model.cc.TypesFolder):
            if t._readOnly:
                continue
            if len(t._definition.strip()) == 0:  # skip empty declarations
                continue
            pf.writeln('//type definition for {}'.format(t._name))
            pf.writeln('{}'.format(t._definition))
            pf.writenl()

        #write forward references
        self.WriteForwards(pf)

        #write prolog user definitions
        #self.WriteUserProlog()

        #write clases includes without inlines
        for cls in self.sorted_classes:
            if cls.is_external:
                continue
            pf.writeln('#include "{name}.h"'.format(name=cls._name))
        pf.writenl()
        pf.writeln('#define INCLUDE_INLINES')

        #write class includes again for inlines
        for cls in self.sorted_classes:
            if cls.is_external:
                continue
            pf.writeln('#include "{name}.h"'.format(name=cls._name))

        #write modules includes
        pf.writenl()
        for module in self.modules:
            if module.inner_library:
                continue
            pf.writeln('#include "{name}.h"'.format(name=module._header))

        #write end safeguard
        pf.writenl()
        pf.writeln('#endif //{name}_H_INCLUDED'.format(name=safe_name))
        pf.writenl()
        f.close()
        self._lastHdrTime = os.path.getmtime(fname)
        return True

    @tran.DelayedMethod
    def ExportCppCodeFiles(self, force=False, logger=None):
        """Do export c++ files"""
        # create sorted main classes list
        self.SortClasses()
        # create the master include file?
        if self._useMaster:
            if not self.WriteMasterHeader(force, logger):
                return
        if self._useMakefile:
            self.WriteMakefile()
        # generate through main classes
        for obj in self.sorted_classes:
            if obj.is_external:
                continue
            obj.updateSources(force)
            if logger is not None:
                e = "Generate source for class " + obj._name
                logger.AppendReportLine(e, wx.OK)
            obj.updateHeaders(force)
            if logger is not None:
                e = "Generate include for class " + obj._name
                logger.AppendReportLine(e, wx.OK)

        # remove temps
        delattr(self, 'sorted_classes')
        # generate through modules
        for obj in [x for x in self.modules if not x.inner_library]:
            obj.updateSources(force)
            if logger is not None:
                e = "Generate source for class " + obj._name
                logger.AppendReportLine(e, wx.OK)
            obj.updateHeaders(force)
            if logger is not None:
                e = "Generate include for class " + obj._name
                logger.AppendReportLine(e, wx.OK)

    @property
    def dir(self):
        """return the project directory"""
        return self._dir

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        stack = tran.TransactionStack
        if self._language == 'c++':
            method = self.ExportCppCodeFiles.inner
        else:
            method = self.ExportPythonCodeFiles.inner
        if method not in stack.delayedCallsFiltered:
            stack.delayedCallsFiltered.append(method)
        super(Project, self).OnUndoRedoRemoving()
        context.App().RemoveProject(self)

    @tran.DelayedMethod
    def ExportPythonCodeFiles(self, force=False, logger=None):
        """Do export python files"""
        logger and logger.AppendReportLine('exporting code files', wx.ICON_INFORMATION)
        for obj in self.packages:
            if obj.parent.inner_package:
                continue
            obj.ExportPythonCodeFiles(force, logger)
        for obj in self.modules:
            if obj.parent.inner_package:
                continue
            obj.ExportPythonCodeFiles(force, logger)

    def ExportCodeFiles(self, force=False, logger=None):
        """Exports all the source code for the project"""
        # create target directories if needed
        if not self.RegisterOutputDirs(logger):
            return
        if self._language == 'c++':
            self.ExportCppCodeFiles(force, logger)
        else:
            self.ExportPythonCodeFiles(force, logger)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        context.App().AddProject(self)
        super(Project, self).OnUndoRedoAdd()

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        if self._language == 'c++':
            return rc.GetBitmap('cppproject')
        else:
            return rc.GetBitmap('python')

    @property
    def bitmap_index(self):
        """Index of tree image"""
        if self._language == 'c++':
            return rc.GetBitmapIndex('cppproject')
        else:
            return rc.GetBitmapIndex('python')

    @property
    def buildable(self):
        """The project may be built?"""
        return self._language in ['c++']

    def __getstate__(self):
        """Get the pickle context. The projects are always
        stored with independence of the workspace container"""
        state = dict(self.__dict__)
        state['_parent'] = None
        return state

    def __setstate__(self, d):
        """In general, if we change something in any class,
        the serialization of old model objects requires this
        filter. When the model handles serialization in an autommated
        fashion, this would be automatically done, based on element
        version."""
        if '_bookmarks' not in d:
            d['_bookmarks'] = {}
        if '_breakpoints' not in d:
            d['_breakpoints'] = {}
        # Do we need to store expressions? At first, it looks interesting,
        # but, what happens if some evil expression hangs our debugging sessions?
        # It's better to provide a facility for loading/storing debugger environment
        # later.
        self.__dict__ = d

    def SetModified(self, bModified=True):
        """Set the modified state"""
        self._lastHdrTime = None
        self._modified = bModified

    def IsModified(self):
        """Get the modified state"""
        return self._modified

    def import_python_dir(self, parent, path, progress=None):
        """Import the contents of the path into the project.
        The parent argument must be the self project or any existent package.
        The contents of the path and recursively scanned subdirs will be copied
        into the directory corresponding to the parent.
        This method will fail if path belongs to the project."""

        # check that path is not inside parent
        target = os.path.realpath(parent.dir)
        path = os.path.realpath(path)
        if len(path) >= len(target) and target == path[:len(target)]:
            raise ValueError('path must be not contained in target')

        for element in os.listdir(path):
            #skip hidden elements
            if element[0] == '.':
                continue
            if len(element) > 1:
                if element[-2:] == '.o':
                    continue
                if len(element) > 3:
                    if element[-4:] in ['.pyc', '.obj', '.sbr']:
                        continue
            abspath = os.path.join(path, element)
            if progress:
                progress.m_text.SetValue('working now on {}'.format(abspath))
                wx.YieldIfNeeded()
            if os.path.isdir(abspath):
                #skip __pycache__
                if element == '__pycache__':
                    continue
                new_directory = os.path.join(target, element)
                try:
                    if not os.path.exists(new_directory):
                        os.makedirs(new_directory)
                except:
                    # very bad thing happens
                    wx.MessageBox('failed creating dir {}'.format(new_directory))
                    continue
                #create a package and iterate
                kwargs = {'parent': parent, 'name': element,
                    'noinit': True}
                package = model.py.Package(**kwargs)
                self.import_python_dir(package, abspath, progress)
                continue
            if not os.path.isfile(abspath):
                # may be a link or a block device ... skip
                continue
            # Ok, create the same file
            new_file = os.path.join(target, element)
            if os.path.exists(new_file):
                # since the file already exists, we must ask user
                choice = wx.MessageBox(
                    'The file {} already exists. Overwrite it?'.format(element),
                    'Attention', wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION, parent=context.frame)
                if choice == wx.NO:
                    continue
                if choice == wx.CANCEL:
                    return False
            # copy the file
            try:
                shutil.copyfile(abspath, new_file)
            except:
                # very bad thing happens
                wx.MessageBox('failed creating file {}'.format(new_file))
                continue
            if self.py_file_pattern.match(element):
                #create new module
                if progress:
                    progress.m_text.SetValue('import {}'.format(abspath))
                    wx.YieldIfNeeded()
                with open(abspath, "r") as module_file:
                    content = module_file.read()
                kwargs = {'parent': parent, 'name': element[:-3],
                    'content': content}
                module = model.py.Module(**kwargs)
                if not module.analize():
                    module.Delete()
        return True

    def update_from_sources(self, **kwargs):
        """read sources and update model"""
        src_dir = kwargs.get('dir', self._dir)  # this is the root dir
        src_dir = os.path.abspath(src_dir)
        target_dir = os.path.abspath(self._dir)
        # ensure the dir exists
        import traceback
        import sys
        try:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            progress = kwargs.get('progress', None)
            if self._language == 'python':
                analytic.pyparse.set_project(self)
                if self.import_python_dir(self, src_dir, progress):
                    # refresh vincled files
                    self.RefreshProjectFiles()
        except Exception, e:
            wx.MessageBox('Failed : {}'.format(e), 'Error', wx.OK | wx.ICON_ERROR)
            traceback.print_exc(file=sys.stdout)
            print type(e)     # the exception instance
            print e.args      # arguments stored in .args
            print e
            return False
        return True

    def RefreshProjectFiles(self):
        """Refresh the files contained in a sngle projec"""
        # The project itself represents the root directory
        # so we need to scan the root dir
        _dir = os.path.realpath(self._dir)
        if not os.access(_dir, os.R_OK):
            return False
        # create a temporal dictionnary
        r = os.path.realpath
        j = os.path.join
        if self._language == 'c++':
            plc = self.level_classes
            s = self.sources_dir
            self.cpp_set = dict([(r(j(s, '{}.cpp'.format(c._name))), c) for c in plc])
            s = self.headers_dir
            self.h_set = dict([(r(j(s, '{}.h'.format(c._name))), c) for c in plc])
        elif self._language == 'python':
            self.file_dict = dict([(r(j(x.dir, '{x._name}.py'.format(x=x))), x)
                for x in self.modules])
            self.file_dict.update([(r(j(x.dir, '__init__.py')), x)
                for x in self.packages])

        # list all files excludding hidden files
        hidden = re.compile(r'\.(.)*')
        project = re.compile(r'(.)*\.pcc')
        excluded = [hidden, project]
        _fset = [s for s in os.listdir(_dir) if not any(y.match(s) for y in excluded)]
        kwargs = {'parent': self}
        knowns = self[model.file.File] + self[model.file.Dir]
        name_knowns = dict([(x.abs_file, x) for x in knowns])
        for f in _fset:
            element = os.path.join(_dir, f)
            if element in name_knowns:
                name_knowns[element].Refresh()
                del name_knowns[element]
                continue
            kwargs['file'] = element
            if os.path.isdir(element):
                model.file.Dir(**kwargs).Refresh()
            else:
                model.file.File(**kwargs).Refresh()
        # remove unexistent file
        for k in name_knowns:
            name_knowns[k].Delete()
        if self._language == 'c++':
            del self.cpp_set
            del self.h_set
        elif self._language == 'python':
            del self.file_dict


