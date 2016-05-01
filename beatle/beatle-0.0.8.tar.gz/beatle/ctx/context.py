# -*- coding: utf-8 -*-
import wx
from deco import classproperty


class context(object):
    """context is a required class for dealing between datamodel
    and rendering"""
    _app = None
    _config = None

    def __init__(self):
        """init"""
        pass

    @classmethod
    def App(cls):
        """return the app"""
        return cls._app

    @classmethod
    def SetApp(cls, app):
        """set the app"""
        cls._app = app

    @classmethod
    def Config(cls):
        """Get config"""
        return cls._config

    @classmethod
    def GetMRU(cls):
        """Get the mru"""
        return cls._mru

    @classmethod
    def RenderUndoRedoAdd(cls, obj):
        """render undo/redo"""
        raise "not implemented"

    @classmethod
    def RenderLoadedAdd(cls, obj):
        """render loaded add"""
        raise "not implemented"

    @classmethod
    def RenderUndoRedoRemoving(cls, obj):
        """render undo/redo"""
        raise "not implemented"

    @classmethod
    def RenderUndoRedoChanged(cls, obj):
        """render undo/redo"""
        raise "not implemented"

    @classmethod
    def Destroy(cls):
        """Destroy context"""
        mru = cls.GetMRU()
        mru.Save(cls.Config())
        cls.frame.SaveViews()
        cls.Config().Flush()
        cls.frame.Destroy()


class localcontext(context):
    """context for doing local works"""
    _frame = None

    @classproperty
    def frame(cls):
        """accessor for frame"""
        return cls._frame

    def __init__(self):
        """init"""
        super(localcontext, self).__init__()
        pass

    @classmethod
    def SetApp(cctx, app):
        """Sets the app and starts the config (may be started after app)
           cctx : context class
           app  : application object"""
        context.SetApp(app)
        cctx._config = wx.Config('beatle.local', vendorName='melvm',
            style=wx.CONFIG_USE_LOCAL_FILE)
        cctx._config.SetPath('~/.config')
        cctx._mru = wx.FileHistory()
        cctx._mru.Load(cctx.Config())

    @classmethod
    def SetFrame(cctx, frame):
        """Set frame window"""
        cctx._frame = frame

    @classmethod
    def SaveProject(cctx, proj):
        """Save all changes"""
        book = cctx.frame.docBook
        for i in range(0, book.GetPageCount()):
            pane = book.GetPage(i)
            if hasattr(pane, '_object'):
                if pane._object.project == proj:
                    pane.Commit()
        cctx.App().SaveProject(proj)

    @classmethod
    def RenderUndoRedoAdd(cctx, obj):
        """render undo/redo"""
        #update old models
        if not hasattr(obj, '_visibleInTree'):
            obj._visibleInTree = True
        #end old models
        if obj._visibleInTree:
            cctx.frame.DoRenderAddElement(obj)

    @classmethod
    def RenderLoadedAdd(cctx, obj):
        """render loaded add"""
        #update old models
        if not hasattr(obj, '_visibleInTree'):
            obj._visibleInTree = True
        #end old models
        if obj._visibleInTree:
            cctx.frame.DoRenderAddElement(obj)

    @classmethod
    def RenderUndoRedoRemoving(cctx, obj):
        """render undo/redo"""
        if obj._visibleInTree:
            cctx.frame.DoRenderRemoveElement(obj)

    @classmethod
    def RenderUndoRedoChanged(cctx, obj):
        """render undo/redo"""
        cctx.frame.UpdateElement(obj)

