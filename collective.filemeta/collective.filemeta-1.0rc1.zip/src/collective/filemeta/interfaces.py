# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IFileMetaProvided(Interface):
   "marker interface for custom types for which file metadata should be processed"


# browser layers for each profile

class IFileMetaLayer(IDefaultBrowserLayer):
   """Marker interface set when collective.filemeta package is installed"""

class ICustomTypeLayer(IDefaultBrowserLayer):
   """Additionally set when the custom type profile is installed"""

class IExtendedFileLayer(IDefaultBrowserLayer):
   """Additionally set when the extended File profile is installed"""


# metadata provider

class IFileMetaProvider(Interface):
   """Provide metadata as a dict grouped (nested) by standard, ie. dc, exif, iptc, xmp...
   If/when metadata supported by a provider is not found on the file, a None value must
   be returned rather than omitting the metadata field.
   """

   def get_metadata(self, data, mimetype, filename):
      """Return metadata dict; use None to indicate missing data value rather than
      omitting the field/key completely
      """


class IContentMetaUpdater(Interface):
   """Update metadata sourced from a particular type of file. It is the responsibility of
   the updater to change any metadata None values to something accepted by Plone as
   'empty', ie. such as '' for textual fields such as Plone Title or Description.
   """

   def update_content(self, obj, metadata):
      "update the content with metadata; convert None values to something that's empty"


class IFileMetaUpdater(Interface):
   "updater that provides round-tripping, ie. copying metadata back to the file"

   # note: this is an advanced use case for which there are no known implementations

   def update_file(self, filedata, metadata):
      "update the source file with metadata"

