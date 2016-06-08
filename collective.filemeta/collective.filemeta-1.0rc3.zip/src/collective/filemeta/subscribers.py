from .behaviors import IMetaFromFile
from .interfaces import IFileMetaProvided

def update_meta_from_file(obj, evt):
   "update content object metadata from primary (document) file field"

   if IFileMetaProvided.providedBy(obj):
      behavior = IMetaFromFile(obj)
      behavior.update_content(evt)

