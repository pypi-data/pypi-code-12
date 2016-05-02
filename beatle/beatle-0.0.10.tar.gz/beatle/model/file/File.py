# -*- coding: utf-8 -*-
import re
import os
import wx
import model
import tran
import ostools


class File(model.TCommon, tran.TransactionFSObject):
    """Declares a file with transactional support"""
    def __init__(self, **kwargs):
        """init"""
        _file = kwargs['file']
        if not os.path.exists(_file):
            with open(_file, 'a'):
                os.utime(_file, None)
        if 'name' not in kwargs:
            kwargs['name'] = os.path.split(_file)[1]
        kwargs['uri'] = kwargs['parent'].project
        super(File, self).__init__(**kwargs)
        self._generator = None
        self.refresh_generator()
        if self._generator:
            self._readOnly = type(self._generator) not in [model.py.Module]

    def __getstate__(self):
        """Dispatch pickle context"""
        state = super(File, self).__getstate__()
        state['_version'] = 0
        return state

    @property
    def breakpoints(self):
        """return the breakpoints attached to the current file"""
        return self.project.breakpoints(self)

    @property
    def bookmarks(self):
        """return the bookmarks attached to the current file"""
        return self.project.bookmarks(self)

    def Refresh(self):
        """refresh file"""
        if not hasattr(self, '_generator'):
            self._generator = None
        self.refresh_generator()
        self._readOnly = bool(self._generator and
            type(self._generator) not in [model.py.Module])

    def GetText(self):
        """Returns file contents"""
        with open(self.abs_file, "r") as f:
            data = f.read()
        return data

    def SetText(self, text):
        """Change text contents"""
        with open(self.abs_file, "w") as f:
            f.truncate(0)
            f.write(text.encode('utf-8'))
        if not self._generator:
            return
        # if the generator is python, it may be a module or package
        if type(self._generator) is model.py.Module:
            self._generator.SaveState()
            self._generator._content = text.encode('utf-8')
            self._generator.analize()

    def refresh_generator(self):
        """Any file may correspond to any generator that resides in a model.
        This method finds the responsible generator and do alink with it"""
        project = self.project
        r = os.path.realpath
        j = os.path.join
        if project._language == 'c++':
            if re.match(r'(.)*\.cpp', self._file):
                if self._generator and self._generator.abs_path_source == self.abs_file:
                    return
                try:
                    cpp_set = project.cpp_set
                except:
                    s = project.sources_dir
                    plc = project.level_classes
                    cpp_set = dict([(r(j(s, '{}.cpp'.format(c._name))), c) for c in plc])
                generator = cpp_set.get(self.abs_file, None)
                if generator is not self._generator:
                    if self._generator:
                        self._generator.set_source(None)
                    self._generator = generator
                    if self._generator:
                        self._generator.set_source(self)
            elif re.match(r'(.)*\.h', self._file):
                if self._generator and self._generator.abs_path_header == self.abs_file:
                    return
                try:
                    h_set = project.h_set
                except:
                    s = project.headers_dir
                    plc = project.level_classes
                    h_set = dict([(r(j(s, '{}.h'.format(c._name))), c) for c in plc])
                generator = h_set.get(self.abs_file, None)
                if generator is not self._generator:
                    if self._generator:
                        self._generator.set_header(None)
                    self._generator = generator
                    if self._generator:
                        self._generator.set_header(self)
        elif project._language == 'python':
            if re.match(r'(.)*\.py', self._file):
                if self._generator and self._generator.abs_path == self.abs_file:
                    return
                try:
                    file_dict = project.file_dict
                except:
                    file_dict = dict([(r(j(x.dir, '{x._name}.py'.format(x=x))), x)
                        for x in project.modules])
                    file_dict.update([(r(j(x.dir, '__init__.py')), x)
                        for x in project.packages])
                generator = file_dict.get(self.abs_file, None)
                if generator is not self._generator:
                    if self._generator:
                        self._generator.set_file(None)
                    self._generator = generator
                    if self._generator:
                        self._generator.set_file(self)

    @property
    def bitmap_index(self):
        """Returns tree image id"""
        try:
            return ostools.MimeHandler.file_image_index(self.abs_file)
        except:
            return wx.NOT_FOUND

    @property
    def is_binary(self):
        """Check if this is a binary file"""
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
        with open(self.abs_file, "r") as f:
            for line in f:
                if is_binary_string(line):
                    return True
        return False

    def Delete(self):
        """Delete """
        #new version
        if self._generator:
            if type(self._generator) is model.cc.Class:
                if hasattr(self._generator, '_header_obj') and self._generator._header_obj == self:
                    self._generator.set_header(None)
                if hasattr(self._generator, '_source_obj') and self._generator._source_obj == self:
                    self._generator.set_source(None)
        super(File, self).Delete()
