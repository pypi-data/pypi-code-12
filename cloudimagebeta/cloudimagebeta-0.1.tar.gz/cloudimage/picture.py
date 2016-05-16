import subprocess
import json
import math
import os
from PIL import Image, ImageStat, ImageDraw, ExifTags
from PIL.ExifTags import TAGS
from collections import Counter
import humanize
import exifread


class Picture:
    def __init__(self, path):
        self.path = path
        self.file = Image.open(self.path)

    def check_extensions(self):
        extensions = ('JPEG', 'TIFF', 'PNG', )
        process = subprocess.Popen(['file', self.path],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        file_name, the_rest = out.decode('utf8').split(': ', 1)
        file_type = the_rest.split(' ', 1)[0]
        if file_type in extensions:
            return True
        else:
            return False

    def get_size(self):
        cropped_path = os.path.join(os.getcwd(), self.path)
        return humanize.naturalsize(os.path.getsize(cropped_path))

    def get_resolution(self):
        width, height = self.file.size
        return '{} x {} pix'.format(width, height)

    def get_orientation(self):
        width, height = self.file.size
        if width > height:
            return 'horizontal'
        elif width < height:
            return 'vertical'
        else:
            return 'square'

    def get_bits(self):
        mode_to_bpp = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24,
                       'RGBA': 32, 'CMYK': 32, 'YCbCr': 24,
                       'I': 32, 'F': 32}
        bpp = mode_to_bpp[self.file.mode]
        return bpp

    def get_is_colored(self):
        stat = ImageStat.Stat(self.file)
        if sum(stat.sum)/3 == stat.sum[0]:
            return 'False'
        else:
            return 'True'

    def get_dominant_colors(self):
        size = width, height = self.file.size
        colors = self.file.getcolors(width * height)
        mcommon = [ite for ite, it in Counter(colors).most_common(3)]
        a = [y for x, y in mcommon]
        return ''.join(repr(e) for e in a)

    def get_exif(self):
        info = self.file._getexif() 
        return {TAGS.get(tag): value for tag, value in info.items()}