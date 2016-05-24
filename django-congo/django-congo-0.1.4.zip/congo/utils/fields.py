# -*- coding: utf-8 -*-
from PIL import Image
from congo.utils.classes import BlankImage
from django.conf import settings
from django.db.models import ImageField, signals
from django.db.models.fields.files import ImageFieldFile
from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri
from django.utils.safestring import mark_safe
import math
import os
import re
import urlparse
from django.utils.crypto import get_random_string
from congo.utils.text import slugify

class MultisizeImageFieldFile(ImageFieldFile):
    FIT = 1
    FILL = 2
    CROP = 3

    def save(self, name, content, save = True):
        if "." in name:
            base, ext = name.rsplit('.', 1)
            name = '%s-original.%s' % (base, ext)
        else:
            name = '%s-original' % name
        super(MultisizeImageFieldFile, self).save(name, content, save)

    def delete(self, save = True):
        self._delete_resized()

        super(MultisizeImageFieldFile, self).delete(save)

    def _get_mode(self, crop = False, fill = False):
        if crop:
            return self.CROP
        elif fill:
            return self.FILL
        return self.FIT

    def _get_size(self, max_width, max_height = None, mode = FIT):
        try:
    #        print ""
    #        print "name", self.name
    #        print "mode", mode

            if not isinstance(max_width, int):
                max_width = settings.CONGO_DEFAULT_IMAGE_WIDTH

            if not isinstance(max_height, int):
                max_height = settings.CONGO_DEFAULT_IMAGE_HEIGHT

    #        print "max_width", max_width
    #        print "max_height", max_height
    #        print "self.width", self.width
    #        print "self.height", self.height

            if mode == self.FILL:

                if self.width > max_width and self.height > max_height:
                    scale = self.width / float(max_width)
                    width = max_width
                    height = int(self.height / scale)

                    if height < max_height:
                        scale = self.height / float(max_height)
                        height = max_height
                        width = int(self.width / scale)
                elif self.width > max_width:
                    scale = self.width / float(max_width)
                    width = max_width
                    height = int(self.height / scale)
                elif self.height > max_height:
                    scale = self.height / float(max_height)
                    height = max_height
                    width = int(self.width / scale)
                else:
                    width = self.width
                    height = self.height

            elif mode == self.CROP:

                if self.width > max_width:
                    width = max_width
                else:
                    width = self.width

                if self.height > max_height:
                    height = max_height
                else:
                    height = self.height

            elif mode == self.FIT:

                if self.width > max_width or self.height > max_height:
                    self_scale = 1. * self.width / self.height
                    max_scale = 1. * max_width / max_height

    #                print "self_scale", self_scale
    #                print "max_scale", max_scale

                    if max_scale < self_scale:
                        if self.width > max_width:
                            scale = 1. * self.width / max_width
                            width = max_width
                            height = int(self.height / scale)
                        else:
                            width = self.width
                            height = self.height

                        if height > max_height:
                            scale = 1. * height / max_height
                            height = max_height
                            width = int(width / scale)
                    else:
                        if self.height > max_height:
                            scale = 1. * self.height / max_height
                            height = max_height
                            width = int(self.width / scale)

                        else:
                            width = self.width
                            height = self.height

                        if width > max_width:
                            scale = 1. * width / max_width
                            width = max_width
                            height = int(height / scale)
                else:
                    width = self.width
                    height = self.height

    #        print "# final"
    #        print "width", width
    #        print "height", height

            return (width, height)
        except IOError:
            return (max_width, max_height)

    def _paste_watermark(self, image, width, height):
        if width > settings.CONGO_WATERMARK_MIN_WIDTH and height > settings.CONGO_WATERMARK_MIN_HEIGHT:
            if hasattr(self, 'watermark') and self.watermark:
                watermark = Image.open(os.path.join(settings.CONGO_WATERMARK_PATH, self.watermark))

                # @FG to powinno być bardziej customizowalne
                # wm na cala szerokosc, lub w rogu, na srodku lub na dole...

#                watermark_width = width - 20
#                watermark_height = int(watermark.size[1] * watermark_width / float(watermark.size[0]))
#                watermark = watermark.resize((watermark_width, watermark_height), Image.ANTIALIAS)

                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                layer = Image.new('RGBA', image.size, (0, 0, 0, 0))

                position = (width - watermark.size[0] - 20, height - watermark.size[1] - 20)
                layer.paste(watermark, position)

                image = Image.composite(layer, image, layer)
        return image

    def _resize(self, path, width, height, mode = FIT):
        image = Image.open(self.path)

        if mode == self.CROP:
            _width, _height = self._get_size(width, height, self.FILL)
            image = image.resize((_width, _height), Image.ANTIALIAS)
            x = int(math.ceil((_width - width) / 2))
            y = int(math.ceil((_height - height) / 2))

            # sprawdzamy, czy moze spowodowac blad, w teorii tak, a w praktyce?
            image = image.crop((x, y, x + width, y + height))
        else:
            image = image.resize((width, height), Image.ANTIALIAS)

        image = self._paste_watermark(image, width, height)
        image.save(path)
        del image

    def _delete_resized(self):
        path, name = os.path.split(self.get_path(self.name))
        pattern = name[::-1].replace("original"[::-1], "(\d+)x(\d+)"[::-1], 1)[::-1]

        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) and re.match(pattern, filename):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

    def get_name(self, width, height):
        return self.name[::-1].replace("original"[::-1], ("%sx%s" % (width, height))[::-1], 1)[::-1]

    def get_path(self, name):
        return os.path.normpath(safe_join(settings.MEDIA_ROOT, name))

    def get_url(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        width, height = self._get_size(max_width, max_height, mode)
        name = self.get_name(width, height)
        path = self.get_path(name)

        if not os.path.isfile(path):
            try:
                self._resize(path, width, height, mode)
            except IOError:
                return BlankImage().get_url(max_width, max_height)
        return urlparse.urljoin(settings.MEDIA_URL, filepath_to_uri(name))

    def get_width(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        return self._get_size(max_width, max_height, mode)[0]

    def get_height(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        return self._get_size(max_width, max_height, mode)[1]

    def render(self, max_width = None, max_height = None, crop = False, **kwargs):
        url = self.get_url(max_width, max_height, crop)
        css_class = kwargs.get('css_class', '')
        alt_text = kwargs.get('alt_text') or ''

        html = """<img src="%s" class="%s" alt="%s" />""" % (url, css_class, alt_text)
        return mark_safe(html)

class MultisizeImageField(ImageField):
    attr_class = MultisizeImageFieldFile

    def __init__(self, verbose_name = None, name = None, watermark_field = None, **kwargs):
        self.watermark_field = watermark_field
        super(MultisizeImageField, self).__init__(verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        super(MultisizeImageField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.update_watermark, sender = cls)

#    def generate_filename(self, instance, filename):
#        directory_name = self.get_directory_name()
#        random_string = get_random_string(4, allowed_chars = 'abcdef0123456789')
#        basename, ext = filename.rsplit('.', 1)
#        filename = self.get_filename("%s.%s" % (slugify(basename), ext))
#        return os.path.join(directory_name, random_string[0:2], random_string[2:4], filename)

    def update_watermark(self, instance, *args, **kwargs):
        image_file = getattr(instance, self.attname)

        if not image_file:
            return

        if self.watermark_field:
            image_file.watermark = getattr(instance, self.watermark_field)
