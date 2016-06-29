# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import re
import os
import model
import tran
import app.resources as rc


class Dir(model.TCommon, tran.TransactionFSObject):
    """Declares a file with transactional support"""
    def __init__(self, **kwargs):
        """init"""
        if 'name' not in kwargs:
            kwargs['name'] = os.path.split(kwargs['file'])[1]
        kwargs['uri'] = kwargs['parent'].project
        super(Dir, self).__init__(**kwargs)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folder")

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex("folder_open")

    def Refresh(self):
        """Refresh the files contained in a sngle projec"""
        # The project itself represents the root directory
        # so we need to scan the root dir

        _dir = self.abs_file
        if not os.access(_dir, os.R_OK):
            return False
        # list all files excludding hidden files
        hidden = re.compile(r'\.(.)*')
        project = re.compile(r'(.)*\.pcc')
        excluded = [hidden, project]
        _fset = [s for s in os.listdir(_dir) if not any(y.match(s) for y in excluded)]
        knowns = self[model.file.File] + self[model.file.Dir]
        name_knowns = dict([(x._file, x) for x in knowns])
        kwargs = {'parent': self}
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
                model.file.File(**kwargs)
        # remove unexistent file
        for k in name_knowns:
            name_knowns[k].Delete()

