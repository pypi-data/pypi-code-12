#!/usr/bin/env python

# standard library impotrs
from contextlib import closing
import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile

# third party related imports
from PIL import Image

# local library imports


def imgoptimize(input_filename, output_filename=None):
    """Optimize image.

    Args:
        input_filename: A string that is the filename of target image
            to optimize.
        output_filename: A string that is the filename of result image
            to store. If None is given, then the optimizied image will
            save in place.

    """

    with closing(Image.open(input_filename)) as im:
        img_format = im.format.lower()

        if im.getbands() == ('C', 'M', 'Y', 'K'):
            kwargs = dict(suffix='.%s' % img_format, delete=False)

            with closing(NamedTemporaryFile(**kwargs)) as f:
                with closing(im.convert('RGB')) as rgb_im:
                    rgb_im.save(f.name)

                input_filename = f.name

    if img_format == 'jpeg':
        optimized_img = _optimize_jpeg(input_filename)
    elif img_format == 'png':
        optimized_img = _optimize_png(input_filename)
    else:
        optimized_img = None

    if optimized_img is not None:
        dst = input_filename if output_filename is None else output_filename
        shutil.move(optimized_img, dst)


def _optimize_jpeg(input_filename):

    f = NamedTemporaryFile(suffix='.jpg', delete=False)
    cmd = ('jpegtran', '-progressive', '-outfile', f.name, input_filename)

    try:
        with closing(open(os.devnull, 'w')) as null:
            subprocess.check_call(cmd, stdout=null, stderr=null)
    except subprocess.CalledProcessError:
        f.close()
        os.unlink(f.name)
        return None

    return f.name


def _optimize_png(input_filename):

    f = NamedTemporaryFile(suffix='.png', delete=False)
    cmd = ('pngcrush', '-rem', 'alla', input_filename, f.name)

    try:
        with closing(open(os.devnull, 'w')) as null:
            subprocess.check_call(cmd, stdout=null, stderr=null)
    except subprocess.CalledProcessError:
        f.close()
        os.unlink(f.name)
        return None

    return f.name
