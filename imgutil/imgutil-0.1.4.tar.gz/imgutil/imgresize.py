#!/usr/bin/env python

# standard library imports
from contextlib import closing

# third party related imports
from PIL import Image

# local library imports


def imgresize(input_filename, width=None, height=None, output_filename=None):
    """Resize an image.

    Args:
        input_filename: A string that is the filename of input image.
        width: An int that is the desired width. If it is None, the
            width is determined by the height to preserve the aspect
            ratio.
        height: An int that is the desired height. If it is None, the
            height is determined by the width to preserve the aspect
            ratio.
        output_filename: A string that is the filename of output image.
            If it is None, the input image will be resized in place.

    """

    if width is None and height is None:
        raise ValueError('width and height are None')

    if width is not None and width <= 0:
        raise ValueError('width must be greater than 0')

    if height is not None and height <= 0:
        raise ValueError('height must be greater than 0')

    with closing(Image.open(input_filename)) as img:
        original_width, original_height = img.size

        if width is None:
            width = int(1.0 * original_width / original_height * height + 0.5)

        if height is None:
            height = int(1.0 * original_height / original_width * width + 0.5)

        with closing(img.resize((width, height), Image.ANTIALIAS)) as resized:
            resized.save(output_filename or input_filename, quality=95)
