from zope.interface import implementer



# base classes for content metadata updater utilities

"""
class MetadataAnnotationsUpdater(object):
   "store any metadata in annotations"

   @staticmethod
   def annotate_metadata(obj, name, value, key=None):
      "store named metadata, optionally under a key (such as dc, exif or iptc)"

      try:
         annotations = IAnnotations(obj)
      except:
         return

      if key:
         if key not in annotations:
            annotations[key] = PersistentDict()
         annotations[key][name] = value
      else:
         annotations[name] = value


class DefaultImageUpdater(object):
   "update the representative thumbnail image"

   @staticmethod
   def update_image(obj, image):
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
"""
