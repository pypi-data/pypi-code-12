from zope.interface import implementer
from zope.annotation import IAnnotations
from persistent.dict import PersistentDict

from plone.namedfile.file import NamedBlobImage

from . import ANNOTATION_KEY

# base classes for content metadata updater utilities


class MetadataAnnotationsUpdater(object):
   "store any metadata in annotations"

   @staticmethod
   def annotate_metadata(obj, name, value, key=None):
      "store named metadata, optionally under a key (such as dc, exif or iptc)"

      try:
         annotations = IAnnotations(obj)
      except:
         return

      try:
        meta = annotations[ANNOTATION_KEY]
      except:
        meta = annotations[ANNOTATION_KEY] = PersistentDict()

      if key:
         if key not in meta:
            meta[key] = PersistentDict()
         meta[key][name] = value
      else:
         meta[name] = value


class DefaultImageUpdater(object):
   "update the representative thumbnail image"

   @staticmethod
   def update_image(obj, image):
      if not image:
         return
      isuffix, idata = image
      itype = isuffix.lower().strip()
      imime = "image/" + isuffix
      ifilename = u"cover" + isuffix
      # if proper image exists, just (re)set the data and file name
      if obj.image:
         obj.image._setData(idata)
         obj.image.filename = ifilename
      # otherwise add a blob image; TODO are there cases when should not use blob?
      else:
         obj.image=NamedBlobImage(data=idata, contentType=imime, filename=ifilename)
