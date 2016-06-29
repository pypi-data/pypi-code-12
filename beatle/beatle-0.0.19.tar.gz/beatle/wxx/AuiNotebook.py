# -*- coding: utf-8 -*-

import wx

TEST_AGW = False

if TEST_AGW:
    import wx.lib.agw.aui as aui
    import wx.lib.agw.aui.auibook as base
else:
    import wx.aui as base


class AuiNotebook(base.AuiNotebook):
    """Aui notebook override due to interfaz/formbuilder collision"""

    def __init__(self, *args, **kwargs):
        """Initialize notebook"""
        super(AuiNotebook, self).__init__(*args, **kwargs)
        if TEST_AGW:
            self.SetAGWWindowStyleFlag(aui.AUI_NB_TAB_FLOAT | aui.AUI_NB_TAB_EXTERNAL_MOVE
            | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_LEFT
            | aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)

    def AddPage(self, *args, **kwargs):
        """We need to shortcut the mistake found to wx interface"""
        if TEST_AGW:
            img_index = None
            pane = args[0]
            if len(args) > 3:
                img_index = args[3]
                args = args[:3]
            if 'bitmap' in kwargs:
                img_index = kwargs['bitmap']
                del kwargs['bitmap']
            if 'disabled_bitmap' in kwargs:
                del kwargs['disabled_bitmap']
            if 'imageId' in kwargs:
                img_index = kwargs['bitmap']
            result = super(AuiNotebook, self).AddPage(*args, **kwargs)
            if img_index:
                page_index = self.GetPageIndex(pane)
                self.SetPageImage(page_index, img_index)
            return result
        if wx.__version__ >= '3.0.0.0':
            if len(args) >= 4:
                if args[3] is wx.NullBitmap:
                    l = list(args)
                    l[3] = wx.NOT_FOUND
                    args = tuple(l)
            else:
                l = list(args)
                l.append(wx.NOT_FOUND)
                args = tuple(l)
            bmp = kwargs.get('bitmap', None)
            if bmp:
                pane = args[0]
                del kwargs['bitmap']
            result = super(AuiNotebook, self).AddPage(*args, **kwargs)
            if bmp:
                page_index = self.GetPageIndex(pane)
                self.SetPageBitmap(page_index, bmp)
            return result


#    def GetCurrentPage(self, *args, **kwargs):
#        """Backward compatibility"""
#        if wx.__version < '3.0.0.0':

