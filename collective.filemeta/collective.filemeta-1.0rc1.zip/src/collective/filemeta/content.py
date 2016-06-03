from plone.autoform import directives
from plone.supermodel import model
from plone.supermodel.directives import primary
from plone.namedfile.field import NamedBlobFile, NamedBlobImage

from . import _


class IDocumentFileSchema(model.Schema):

   directives.omitted('image')

   image = NamedBlobImage(
      title=_(u"label_image", u"Image"),
      description=_("description_image", u"Document image representation")
   )

   primary("file")
   file = NamedBlobFile(
      title=_(u"label_file", u"File"),
      description=_("description_file", u"Document file"),
      required=True
   )

