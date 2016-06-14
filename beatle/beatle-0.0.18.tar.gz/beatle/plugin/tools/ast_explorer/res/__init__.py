# -*- coding: utf-8 -*-
import wx

from _expr import _expr
from _module import _module
from _import import _import
from _str import _str
from _alias import _alias
from _assign import _assign
from _name import _name
from _binop import _binop
from _store import _store
from _load import _load
from _attribute import _attribute
from _add import _add
from _num import _num
from _classdef import _classdef
from _functiondef import _functiondef
from _arguments import _arguments
from _param import _param
from _call import _call
from _dict import _dict
from _return import _return
from _listcomp import _listcomp
from _tuple import _tuple
from _comprehension import _comprehension
from _global import _global
from _for import _for
from _keyword import _keyword
from _if import _if
from _bool import _bool
from _and import _and
from _compare import _compare
from _in import _in
from _subscript import _subscript
from _index import _index
from _unary import _unary
from _not import _not
from _eq import _eq
from _not_eq import _not_eq
from _delete import _delete
from _del import _del
from _sub import _sub
from _not_in import _not_in
from _gte import _gte
from _lte import _lte
from _lt import _lt
from _gt import _gt
from _is import _is
from _is_not import _is_not
from _floor_div import _floor_div
from _continue import _continue
from _try import _try
from _or import _or
from _except import _except
from _print import _print
from _list import _list

_xpm = [_expr, _module, _import, _str, _alias, _assign, _name, _binop, _store, _load,
        _attribute, _add, _num, _classdef, _functiondef, _arguments, _param, _call,
        _dict, _return, _tuple, _listcomp, _comprehension, _global, _for, _keyword,
        _if, _bool, _and, _compare, _in, _subscript, _index, _unary, _not,
        _eq, _not_eq, _delete, _del, _sub, _not_in, _gte, _lte, _lt, _gt, _is,
        _is_not, _floor_div, _continue, _try, _or, _except, _print, _list]

_bitmapList = []


def CreateBitmapList():
    """Crea la lista de bitmaps"""
    global _bitmapList
    global _xpm
    for xpm in _xpm:
        bmp = wx.BitmapFromXPMData(xpm)
        _bitmapList.append(bmp)


def GetBitmapIndex(name, access=None):
    """Return the bitmap index"""
    try:
        base_index = _xpm.index(eval('_{}'.format(name)))
    except:
        return wx.NOT_FOUND
    return base_index


def GetBitmap(name):
    """Get the specific bitmap"""
    index = GetBitmapIndex(name)
    if index == wx.NOT_FOUND:
        raise KeyError('bitmap {} not found'.format(name))
        return None
    global _bitmapList
    if not len(_bitmapList):
        CreateBitmapList()
    return _bitmapList[index]


def GetBitmapImageList():
    """Returns the bitmap image list"""
    global _bitmapList
    if len(_bitmapList) == 0:
        CreateBitmapList()
    imglist = wx.ImageList(16, 16, True, len(_bitmapList))
    for bmp in _bitmapList:
        imglist.Add(bmp)
    return imglist
