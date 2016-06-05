# -*- coding: utf-8 -*-

import mimetypes
import wx
import app.resources as rc
import deco


class MimeHandler(object):
    """Class for handling mime types"""
    instance = None

    def __init__(self):
        """init"""
        import gtk
        import gio
        self._extra_bitmap = {}
        self._handler = wx.MimeTypesManager()
        self._mime = self._handler.EnumAllFileTypes()
        self._mime_themed_icon = dict([(x, gio.content_type_get_icon(x)) for x in self._mime])
        self._themed_icon = []
        for themed_icon in self._mime_themed_icon.values():
            if themed_icon not in self._themed_icon:
                self._themed_icon.append(themed_icon)
        self._theme = gtk.icon_theme_get_default()
        self._size = 24
        self._imageList = None
        self.register_default_extra_bitmaps()
        MimeHandler.instance = self
        super(MimeHandler, self).__init__()

    @deco.classproperty
    def imageList(cls):
        """returns the image list"""
        if not MimeHandler.instance:
            MimeHandler.instance = MimeHandler()
        if not MimeHandler.instance._imageList:
            MimeHandler.instance.realize()
        return MimeHandler.instance._imageList

    def realize(self):
        """ends the construction of the mime handler"""
        self._icons = self._load_icons()
        self._themed_icon_index = self._map_icon_index()
        self._imageList = self._create_image_list()

    def register_default_extra_bitmaps(self):
        """Adds some extra bitmaps that will be included
        in the image list"""
        self._extra_bitmap.update(
            dict([
                (i, wx.BitmapFromXPMData(rc._xpm[i]))
                for i in range(0, len(rc._xpm))]))

    def register_extra_bitmap(self, position, bitmap):
        """Some extra bitmaps may be added to the image list
        at specific positions"""
        self._extra_bitmap[position] = bitmap

    def _load_icons(self):
        """Reload icons for some size and returns a dict"""
        icons = {}
        size = self._size
        for themed_icon in self._themed_icon:
            info = self._theme.choose_icon(themed_icon.get_names(), size, 0)
            if info:
                icons[themed_icon] = wx.Icon(info.get_filename(), desiredWidth=size)
            else:
                icons[themed_icon] = None
        return icons

    def _map_icon_index(self):
        """Create a map for the themed icon and image index"""
        index = 0
        themed_icon_index = {}
        for themed_icon in self._themed_icon:
            if self._icons[themed_icon]:
                # skip registered bitmaps that have fixed positions
                while index in self._extra_bitmap:
                    index = index + 1
                themed_icon_index[themed_icon] = index
                index = index + 1
            else:
                themed_icon_index[themed_icon] = wx.NOT_FOUND
        return themed_icon_index

    def _create_image_list(self):
        """Create an image list based on current icons"""
        index = 0
        icons = [x for x in self._icons.values() if x]
        iml = wx.ImageList(self._size, self._size, True, len(icons))
        for themed_icon in self._themed_icon:
            ico = self._icons[themed_icon]
            if ico is None:
                continue
            while index in self._extra_bitmap:
                iml.Add(self._extra_bitmap[index])
                index = index + 1
            if ico.GetWidth() != self._size or ico.GetHeight() != self._size:
                img = wx.BitmapFromIcon(ico).ConvertToImage()
                sz = wx.Size(self._size, self._size)
                if ico.GetWidth() >= ico.GetHeight():
                    fact = float(self._size) / float(ico.GetWidth())
                    h = int(float(ico.GetHeight()) * fact)
                    img = img.Rescale(self._size, h, wx.IMAGE_QUALITY_NORMAL)
                    pos = wx.Point(0, int((self._size - h) / 2))
                    img = img.Resize(sz, pos)
                else:
                    fact = float(self._size) / float(ico.GetHeight())
                    w = int(float(ico.GetWidth()) * fact)
                    img = img.Rescale(w, self._size, wx.IMAGE_QUALITY_NORMAL)
                    pos = wx.Point(int((self._size - w) / 2), 0)
                    img = img.Resize(sz, pos)
                bmp = img.ConvertToBitmap()
                iml.Add(bmp)
            else:
                iml.AddIcon(ico)
            index = index + 1
        return iml

    @classmethod
    def file_image_index(cls, path):
        """Returns the associated image index or wx.NOT_FOUND, based
        on mime type"""
        self = cls.instance
        use_gtk = True  # gtk mime-resolution is much better than extension-based
        if use_gtk:
            import gio
            f = gio.File(path)
            info = f.query_info('standard::content-type')
            mime = info.get_content_type()
        else:
            mime = mimetypes.guess_type(path)[0]
        if not mime:
            return wx.NOT_FOUND
        if mime not in self._mime:
            return wx.NOT_FOUND
        # ok, we can go from mime to themed icon and from that to icon index
        themed = self._mime_themed_icon[mime]
        return self._themed_icon_index[themed]
