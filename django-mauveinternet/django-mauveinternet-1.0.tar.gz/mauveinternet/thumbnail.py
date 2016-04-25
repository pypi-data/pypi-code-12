"""Provides built-in thumbnailing of uploaded images at the model level.

>>> class Photo(models.Model):
...     user = models.ForeignKey(User)
...     image = ThumbnailField(thumbnails={'small': Thumbnail(w=150, h=150), 'rounded': RoundedThumbnail(w=150, h=150, radius=5)})
...     def get_image_upload_to(self):
...         return 'user-photos/%s/' % self.user.username
...
>>> p = Photo(user=user)
>>> p.save_image_file('foo.jpg', data)
>>> p.save()
>>> p.get_image_rounded_url()
/assets/user-photos/theusersname/rounded(foo).jpg
"""

import re
import os
import os.path
import urllib

from cStringIO import StringIO
from django.conf import settings

from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


from PIL import Image, ImageOps, ImageDraw, ImageColor
from PIL import ImageFile as PILImageFile


class ThumbnailFile(object):
    def __init__(self, imagefile, name, thumbnailer):
        self.imagefile = imagefile
        self.thumbname = name
        self.thumbnailer = thumbnailer

    def negotiate_output_format(self, ext):
        if ext.lower() in ['.png', '.gif']:
            if self.thumbnailer.output_alpha() != Thumbnail.FLATTEN_ALPHA:
                return 'PNG'
        else:
            if self.thumbnailer.output_alpha() == Thumbnail.CREATE_ALPHA:
                return 'PNG'
        return 'JPEG'

    def get_filename(self, filename):
        stem, ext = os.path.splitext(filename)

        if self.negotiate_output_format(ext) == 'JPEG':
            t_ext = 'jpg'
        else:
            t_ext = 'png'

        return '%s.%s.%s' % (stem, self.thumbname, t_ext)

    def generate_filename(self, filename):
        dirname, basename = os.path.split(filename)
        return os.path.join(dirname, self.get_filename(basename))

    def save_thumbnail(self, im_inp):
        im_out = self.thumbnailer.thumbnail(im_inp)
        f = StringIO()
        if self.name.endswith('.jpg'):
            im_out.save(f, 'JPEG')
        else:
            im_out.save(f, 'PNG')
        f.seek(0)

        self.imagefile.storage.save(self.name, ContentFile(f.read()))
        f.close()

    def _name(self):
        return self.generate_filename(self.imagefile.name)
    name = property(_name)

    def _url(self):
        self.imagefile._require_file()
        return self.imagefile.storage.url(self.name)
    url = property(_url)


class ImageFileWithThumbnails(ImageFieldFile):
    def __init__(self, instance, field, name):
        super(ImageFileWithThumbnails, self).__init__(instance, field, name)

        self.thumbnails = []
        for k in field.thumbnails:
            tf = ThumbnailFile(self, k, field.thumbnails[k])
            self.thumbnails.append(tf)
            setattr(self, k, tf)

    def __getattr__(self, k):
        if k in object.__getattr__(self, 'field').thumbnails:
            return ThumbnailFile(self, k, self.field.thumbnails[k])
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__, k))

    def save(self, name, content, save=True):
        super(ImageFileWithThumbnails, self).save(name, content, save=False)
        self.build_thumbnails(name, self)

        if save:
            self.instance.save()

    def rebuild_thumbnails(self):
        self.build_thumbnails(self.name, self)

    def build_thumbnails(self, name, content):
        if not self.field.thumbnails:
            return

        content.open(mode='r')
        im = Image.open(content)        #incremental loader is buggy
        if im.mode not in ['L', 'RGB', 'RGBA']:
            im = im.convert('RGBA')

        for k in self.field.thumbnails:
            thumbnailfile = getattr(self, k)
            self.storage.delete(thumbnailfile.name)
            thumbnailfile.save_thumbnail(im.copy()) #thumbnail a copy (Image.thumbnail operates in-place)

    def delete(self, save=True):
        self.delete_thumbnails()
        super(ImageFileWithThumbnails, self).delete(save)

    def delete_thumbnails(self):
        """Deletes all thumbnails for a given image."""
        for thumbnailfile in self.thumbnails:
            self.storage.delete(thumbnailfile.name)


class ThumbnailImageField(ImageField):
    attr_class = ImageFileWithThumbnails

    def __init__(self, thumbnails, *args, **kwargs):
        super(ThumbnailImageField, self).__init__(*args, **kwargs)
        self.thumbnails = thumbnails

    def deconstruct(self):
        name, path, args, kwargs = super(ThumbnailImageField, self).deconstruct()
        args = [self.thumbnails] + args
        return name, path, args, kwargs


@deconstructible
class Thumbnail(object):
    """The default thumbnailer, and the base class of other thumbnailers.

    Each Thumbnail handles the generation, but not the file handling, of the
    thumbnails for a ThumbnailImageField.
    """

    def __init__(self, w=None, h=None):
        if w is None:
            w = 32768       #Infinity!
        if h is None:
            h = 32768       #Infinity!
        self.dims = (w, h)

    PRESERVE_ALPHA = 0      # outputs an alpha channel if and only if the input provided an alpha channel
    CREATE_ALPHA = 1        # always outputs an alpha channel
    FLATTEN_ALPHA = 2       # never outputs an alpha channel

    def output_alpha(self):
        """Return a constant representing the behaviour of this thumbnailer
        instance with respect to the input alpha.

        The ThumbnailImageField uses this to negotiate whether to generate JPEG or PNG
        thumbnails. RGB thumbnails are saved as JPEGs, RGBA thumbnails as PNGs.
        """
        return Thumbnail.PRESERVE_ALPHA

    def thumbnail(self, im):
        """Called to actually perform the thumbnailing of the object."""
        size = im.size
        if size[0] < self.dims[0] and size[1] < self.dims[1]:
            return im
        im.thumbnail(self.dims, Image.ANTIALIAS)
        return im


@deconstructible
class ZoomToFitThumbnail(Thumbnail):
    """Generates thumbnails at the exact dimensions given, with no border.
    The image is zoomed so as to fit outside the given dimensions, then the
    rectangle required is cropped from the center."""
    def __init__(self, w, h):
        """Override constructor so as not to accept default arguments"""
        self.dims = (w, h)

    def thumbnail(self, im):
        """Called to actually perform the thumbnailing of the object."""
        from math import ceil
        iw, ih = im.size
        aspect = float(iw)/float(ih)

        tw, th = self.dims
        aspect_required = float(tw)/float(th)

        if aspect > aspect_required:
            dh = th
            dw = int(ceil(th * aspect))
            l = (dw-tw)/2
            crop_rect = l, 0, l + tw, th
        else:
            dw = tw
            dh = int(ceil(tw / aspect))
            t = (dh-th)/2
            crop_rect = 0, t, tw, t + th

        if dw < iw or dh < ih:
            sized = im.resize((dw, dh), Image.ANTIALIAS)
        else:
            sized = im.resize((dw, dh), Image.BICUBIC)
        return sized.crop(crop_rect)


@deconstructible
class ZoomingThumbnail(Thumbnail):
    """Generates thumbnails at a given size, but zoomed in
    by a certain factor on the middle of the source image.

    This is primarily useful when generating thumbnails of textures, where the detail is
    lost by the normal thumbnailer."""

    def __init__(self, scale_factor, w=None, h=None):
        super(ZoomingThumbnail, self).__init__(w, h)
        self.scale_factor = scale_factor

    def thumbnail(self, im):
        #TODO: adjust zoom to fit, for non-square images
        zoomed_dims = (self.dims[0] * self.scale_factor,
                                 self.dims[1] * self.scale_factor)
        im.thumbnail(zoomed_dims, Image.ANTIALIAS)
        return im.crop((
                (self.zoomed_dims[0] - self.dims[0])//2,
                (self.zoomed_dims[1] - self.dims[1])//2,
                self.dims[0],
                self.dims[1])
        )


@deconstructible
class RoundedThumbnail(Thumbnail):
    """Generates thumbnails with rounded corners."""
    def __init__(self, radius=10, w=None, h=None):
        super(RoundedThumbnail, self).__init__(w, h)
        self.radius = radius
        self.generateCorners()

    def output_alpha(self):
        return Thumbnail.CREATE_ALPHA

    def generateCorners(self):
        import math
        w = int(math.ceil(self.radius * math.sqrt(0.5)))
        ioff = self.radius - w
        buf = ''
        for j in range(w):
            row = math.sqrt(self.radius ** 2 - (j + 0.5) ** 2)
            i = 0
            while i + ioff < (row-1):
                buf += '\xff'
                i += 1
            frac = (row - math.floor(row))
            buf += chr(int(frac * 255))
            i += 1
            while i < w:
                buf += '\x00'
                i += 1

        q = Image.fromstring('L', (w, w), buf)
        self.br = Image.new('L', (self.radius, self.radius), 'white')
        self.br.paste(q, (ioff, 0))
        q = ImageOps.mirror(q.rotate(270))
        self.br.paste(q, (0, ioff))
        draw = ImageDraw.Draw(self.br)
        draw.rectangle((self.radius-ioff, self.radius-ioff, self.radius, self.radius), fill='black')
        del(draw)

        self.tr = ImageOps.flip(self.br)
        self.tl = ImageOps.mirror(self.tr)
        self.bl = ImageOps.mirror(self.br)

    def generateMask(self, dims):
        mask = Image.new('L', dims, 'white')
        w, h = dims
        for corner, top, left in [(self.tl, 0, 0), (self.tr, 0, w - self.radius), (self.bl, h - self.radius, 0), (self.br, h - self.radius, w - self.radius)]:
            mask.paste(corner, (left, top))
        return mask

    def thumbnail(self, im):
        im.thumbnail(self.dims, Image.ANTIALIAS)

        mask = self.generateMask(im.size)

        buf = Image.new('RGBA', im.size)
        buf.paste(im, (0, 0), mask)
        return buf


@deconstructible
class WatermarkedThumbnail(Thumbnail):
    def __init__(self, watermark, w=None, h=None):
        super(WatermarkedThumbnail, self).__init__(w, h)
        self.watermark = Image.open(os.path.join(settings.MEDIA_ROOT, watermark))
        self.watermark.load()

    def thumbnail(self, im):
        im = super(WatermarkedThumbnail, self).thumbnail(im)
        pos = (im.size[0] - self.watermark.size[0],
               im.size[1] - self.watermark.size[1])

        im.paste(self.watermark, pos, self.watermark)
        return im


@deconstructible
class BackgroundColour(Thumbnail):
    def __init__(self, colour='#fff'):
        self.col = ImageColor.getrgb(colour)

    def output_alpha(self):
        return Thumbnail.FLATTEN_ALPHA

    def thumbnail(self, im):
        background = Image.new('RGB', im.size, self.col)
        background.paste(im, None, im)
        return background


@deconstructible
class ThumbnailStack(Thumbnail):
    def __init__(self, *args):
        self.stack = args

    def output_alpha(self):
        a = Thumbnail.PRESERVE_ALPHA
        for s in self.stack:
            sa = s.output_alpha()
            if sa != Thumbnail.PRESERVE_ALPHA:
                a = sa
        return a

    def thumbnail(self, im):
        for t in self.stack:
            im = t.thumbnail(im)
        return im


def rebuild_all_thumbnails():
    from django.db.models import get_models
    for m in get_models():
        fs = []
        for f in m._meta.fields:
            if isinstance(f, ThumbnailImageField):
                fs.append(f)

        for inst in m._default_manager.all():
            for f in fs:
                file = getattr(inst, f.attname)
                if file:
                    print file.name
                    #print "%s.%s.%s - \"%s\"" % (m._meta.app_label, m._meta.object_name, f.attname, inst)
                    file.rebuild_thumbnails()
