# -*- coding: utf-8 -*-

from persistent.dict import PersistentDict

from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from zope.interface import Interface
from zope.interface import implementer

from plone.namedfile.file import NamedBlobImage
from plone.rfc822.interfaces import IPrimaryFieldInfo

from .interfaces import IFileMetaProvider, IFileMetaProvided, IContentMetaUpdater
from . import logger


class IMetaFromFile(Interface):
   """Marker interface for metadata from file behavior"""


@implementer(IMetaFromFile)
class MetaFromFile(object):
   "behavior to update content metadata from uploaded file"

   def __init__(self, context):
      self.context = context
      info = IPrimaryFieldInfo(context, None)
      if info is None or info.value is None:
         self._file = None
      else:
         self._file = info.value

   def update_content(self):

      # guard
      if not self._file:
         return

      # try to get a metadata provider utility for the content type
      try:
         provider = getUtility(IFileMetaProvider, name=self._file.contentType)
      except ComponentLookupError:
         logger.warn("no metadata provider utility found for %s" % self._file.contentType)
         return

      # and content updater utility, likewise
      try:
         updater = getUtility(IContentMetaUpdater, name=self._file.contentType)
      except ComponentLookupError:
         logger.warn("no metadata updater utility found for %s" % self._file.contentType)
      else:
         meta = provider.get_metadata(self._file.data, self._file.contentType, self._file.filename)
         updater.update_content(self.context, meta)
