"""
This module contains (collective.filemeta) FileMetaProvider & IContentMetaUpdater utility
implementations for PDF documents.

The updater substitutes PDF subject for Plone description, and PDF keywords for Plone
subject. If you do not like this, file an issue or override the utility.

"""

from StringIO import StringIO

from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image

from zope.interface import implementer

from collective.filemeta.interfaces import IFileMetaProvider, IContentMetaUpdater
from collective.filemeta.base import MetadataAnnotationsUpdater, DefaultImageUpdater


@implementer(IFileMetaProvider)
class MetaProvider(object):


   def get_metadata(self, data, mimetype, filename):
      "implement the utility interface"

      self.pdf = PdfFileReader(StringIO(data))
      self.meta = self.pdf.getDocumentInfo()
      self.xmp = self.pdf.getXmpMetadata()

      dc = {
         "title": self.title,
         "subject": self.subject,
         "language": self.language
      }

      return {
         "dc": dc,
         "keywords": self.keywords,
         "image": self.image,
         "pagecount": self.pagecount,
         "mimetype": mimetype,
         "filename": filename
      }


   @property
   def title(self):
      return self.meta["/Title"] if "/Title" in self.meta else ""

   @property
   def subject(self):
      return self.meta["/Subject"] if "/Subject" in self.meta else ""

   @property
   def keywords(self):
      "keywords, tags... "

      # First, try Apple keywords as they are already nicely separated for us
      # Note that meta.get() would return a proxy object, not list of keywords..
      keywords = self.meta["/AAPL:Keywords"] if "/AAPL:Keywords" in self.meta else []

      # If not, split regular keywords string by commas
      if not keywords and self.meta.get("/Keywords"):
         keywords = [kw.strip() for kw in self.meta["/Keywords"].split(',')]

      # If still no keywords, try XMP metadata (should maybe be checked first)
      if not keywords:
         try:
            return [kw.strip() for kw in self.xmp.pdf_keywords.split(',')]
         except:
            pass
         try:
            return [kw.strip() for kw in self.xmp.dc_subject.split(',')]
         except:
            return []

      return keywords

   @property
   def language(self):
      "return xmp language"
      return getattr(self.xmp, "dc_language", "")

   @property
   def pagecount(self):
      "return number of pages/sheets/slides the PDF has"
      return self.pdf.getNumPages()

   @property
   def image(self):
      "return 75dpi representative max 192px high (cover) PNG image for document"
      cover = self.pdf.getPage(0)
      cover_fp = StringIO()
      writer = PdfFileWriter()
      writer.addPage(cover)
      writer.write(cover_fp)
      cover_fp.flush()
      cover_fp.seek(0)
      with Image(file=cover_fp, resolution=(75,75), format="pdf") as img:
         img.format = "png"
         img.transform(resize='x192')
         blob = img.make_blob()

      return ("png", blob)


class ContentUpdater(MetadataAnnotationsUpdater, DefaultImageUpdater):
   "updates dc:title, dc:description, dc:subject, page count and cover image thumbnail"

   def update_content(self, obj, metadata, overwrite=False):
      "implement the utility interface"

      # set title & description & subject if told to or they do not yet exist

      if overwrite or not obj.Title():
         obj.setTitle(metadata["dc"]["title"] or metadata["filename"])

      if overwrite or not obj.Description():
         obj.setDescription(metadata["dc"]["subject"] or "")

      if overwrite or not obj.Subject():
         obj.setSubject(metadata["keywords"] or [])

      self.annotate_metadata(obj, "pagecount", metadata["pagecount"])
      self.update_image(obj, metadata["image"])


