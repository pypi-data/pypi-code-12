from decimal import Decimal

from Acquisition import aq_inner
from zope.annotation import IAnnotations
from zope.component import getAdapter
from plone import api
from plone.namedfile.utils import get_contenttype
from plone.memoize.view import memoize

from Products.Five import BrowserView
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path

#from ..interfaces import IDocumentFile
from .. import logger, ANNOTATION_KEY


class FileMetaDisplay(BrowserView):
   "custom display for files with metadata copied over"

   @memoize
   def iconurl(self):
      "get URL for showing the icon"
      base =  api.portal.get().absolute_url()
      mt = self.mimetype()
      return (base + '/' + guess_icon_path(mt)) if mt else ""

   @memoize
   def mimetype(self):
      "mimetype"
      tool = api.portal.get_tool("mimetypes_registry")
      mt = get_contenttype(self.context.file)
      types = tool.lookup(mt)
      if len(types) == 1:
         return types[0]
      else:
         return None

   @memoize
   def doctype(self):
      "human-readable mime type name"
      mt = self.mimetype()
      return mt.name() if mt else ""

   @memoize
   def size(self):
      "shortcut"
      return self.context.file.size

   @memoize
   def pagecount(self):
      "number of pages"
      try:
         return IAnnotations(self.context)[ANNOTATION_KEY]["pagecount"]
      except:
         return None

   @memoize
   def sizelabel(self):
      "return human-readable size"
      num = self.context.file.size
      suffix = 'B'
      for unit in ['','K','M','G','T','P','E','Z']:
         if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
         num /= 1024.0
      return "%.1f%s%s" % (num, 'Yi', suffix)
