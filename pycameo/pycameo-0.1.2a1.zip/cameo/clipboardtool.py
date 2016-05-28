# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
import win32clipboard as cb
import win32con
#剪貼簿存取
class ClipboardTool:
    
    #將 unicode 字串放入剪貼簿
    def setUnicodeText(self, strUnicode=u""):
        cb.OpenClipboard()
        cb.EmptyClipboard()
        cb.SetClipboardData(win32con.CF_UNICODETEXT, strUnicode)
        cb.CloseClipboard()
        
    #取出 unicode 字串
    def getUnicodeText(self):
        cb.OpenClipboard()
        uText = cb.GetClipboardData(win32con.CF_UNICODETEXT)
        cb.CloseClipboard()
        return uText
        