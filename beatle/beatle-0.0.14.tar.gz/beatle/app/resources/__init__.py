# -*- coding: utf-8 -*-

import wx
import app

from _workspace import _workspace
from _folder import _folder
from _folder_open import _folder_open
from _project import _project
from _class import _class
from _py_class import _py_class
from _friend import _friend
from _method import _method
from _py_method import _py_method
from _classdiagram import _classdiagram
from _member import _member
from _py_member import _py_member
from _constructor import _constructor
from _py_init import _py_init
from _context import _context
from _destructor import _destructor
from _inheritance import _inheritance
from _py_inheritance import _py_inheritance
from _relation import _relation
from _folderT import _folderT
from _folderP import _folderP
from _folderI import _folderI
from _type import _type
from _parent import _parent
from _library import _library
from _child import _child
from _cppfile import _cppfile
from _pyfile import _pyfile
from _hfile import _hfile
from _mfile import _mfile
from _python import _python
from _protected import _protected
from _private import _private
from _target import _target
from _cppproject import _cppproject
from _namespace import _namespace
from _module import _module
from _py_module import _py_module
from _function import _function
from _py_function import _py_function
from _data import _data
from _py_variable import _py_variable
from _enum import _enum
from _tres import _tres
from _py_args import _py_args
from _py_kwargs import _py_kwargs
from _py_import import _py_import
from _models import _models
from _files import _files
from _tasks import _tasks
from _git import _git
from _py_argument import _py_argument
from _py_package import _py_package
from _start import _start
from _info import _info
from _mini_logo import _mini_logo
from _git_repo import _git_repo
from _git_file import _git_file
from _git_file_modified import _git_file_modified
from _git_file_staged import _git_file_staged
from _git_file_deleted import _git_file_deleted
from _file import _file
from _reload import _reload
from _decorator import _decorator
from _bookmark import _bookmark
from _git_remote import _git_remote
from _glass_clock import _glass_clock
from _folder_pendings import _folder_pendings
from _folder_pendings_open import _folder_pendings_open
from _folder_current import _folder_current
from _folder_current_open import _folder_current_open
from _refresh import _refresh
from _run import _run
from _run_file import _run_file
from _stop import _stop
from _debug import _debug
from _debug_file import _debug_file
from _step_into import _step_into
from _step_out import _step_out
from _step_over import _step_over
from _continue import _continue
from _pyboost import _pyboost

#from _class_small import _class_small


_xpm = [
    _class, _constructor, _member, _method, _destructor,
    _inheritance, _type, _parent, _child, _enum, _py_argument,
    _py_args, _py_kwargs, _py_init, _py_member, _py_method,
    _py_inheritance, _classdiagram, _relation, _folderT,
    _cppfile, _hfile, _mfile, _target, _cppproject, _namespace,
    _folder, _folder_open, _project, _module, _function,
    _py_function, _data, _py_variable, _tres, _friend, _folderP,
    _library, _python, _workspace, _context, _py_module,
    _py_package, _py_class, _models, _files, _tasks, _py_import,
    _pyfile, _start, _info, _mini_logo, _git, _git_repo,
    _git_file, _git_file_modified, _git_file_staged,
    _git_file_deleted, _file, _reload, _decorator, _folderI,
    _git_remote, _glass_clock, _folder_pendings, _folder_pendings_open,
    _folder_current, _folder_current_open, _refresh, _run,
    _run_file, _stop, _step_into, _step_out, _step_over, _continue,
    _debug, _debug_file, _pyboost]


_accessed = [_class, _constructor, _member, _method, _destructor, _inheritance,
    _type, _parent, _child, _enum]
_access = {'protected': _protected, 'private': _private}

_bitmapList = []
_bitmapAmodeless = {}

#def ImageIndex(name):
#    """Finds the xpm by name and returns the index (or wx.NOT_FOUND)"""
#    try:
#        return _xpm.index(eval('_{}'.format(name)))
#    except:
#        return wx.NOT_FOUND


def CreateBitmapList():
    """Crea la lista de bitmaps"""
    global _bitmapList
    global _xpm
    global _bitmapAmodeless
    global _accessed
    bmpWithAmodeless = []
    for xpm in _xpm:
        bmp = wx.BitmapFromXPMData(xpm)
        _bitmapList.append(bmp)
        if xpm in _accessed:
            bmpWithAmodeless.append(bmp)
    _bitmapAmodeless['public'] = {}
    for bmp in bmpWithAmodeless:
        _bitmapAmodeless['public'][_bitmapList.index(bmp)] = _bitmapList.index(bmp)
    for access in _access:
        prefixBmp = wx.BitmapFromXPMData(_access[access])
        _bitmapAmodeless[access] = app.SuffixBitmapList(prefixBmp,
            bmpWithAmodeless, _bitmapList)


#def BitmapIndex(name, access=None):
#    """Finds the xpm by name and returns the index (or wx.NOT_FOUND)"""
#    try:
#        return _xpm.index(eval('_{}'.format(name)))
#    except:
#        return wx.NOT_FOUND

#def GetBitmapName(name, access=None):
#    """Return the bitmap index by name"""
#    return GetBitmapIndex(ImageIndex(name), access)

def GetBitmapIndex(name, access=None):
    """Return the bitmap index"""
    try:
        base_index = _xpm.index(eval('_{}'.format(name)))
    except:
        return wx.NOT_FOUND
    if access is None:
        return base_index
    global _bitmapList
    if len(_bitmapList) == 0:
        CreateBitmapList()
    return _bitmapAmodeless[access][base_index]


def GetBitmap(name, access=None):
    """Get the specific bitmap"""
    index = GetBitmapIndex(name, access)
    if index == wx.NOT_FOUND:
        raise KeyError('bitmap {} not found'.format(name))
        return None
    return _bitmapList[index]


def GetBitmapImageList():
    """Returns the bitmap image list"""
    global _bitmapList
    if len(_bitmapList) == 0:
        CreateBitmapList()
    (w, h) = app.GetBitmapMaxSize(_bitmapList)
    if wx.__version__ >= '3.0.0.0':
        w = 0
    imglist = wx.ImageList(w, h, True, len(_bitmapList))
    for bmp in _bitmapList:
        imglist.Add(bmp)
    return imglist

