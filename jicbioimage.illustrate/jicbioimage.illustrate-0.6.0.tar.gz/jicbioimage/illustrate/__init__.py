"""Module for creating illustrations.

To create an annotated image we need an instance of the
:class:`jicbioimage.illustrate.AnnotatedImage` class.

>>> from jicbioimage.illustrate import AnnotatedImage

Suppose that we have an existing image.

>>> from jicbioimage.core.image import Image
>>> im = Image((50,50))

We can use this image to create an canvas instance populated with the data
as a RGB gray scale image.

>>> canvas = AnnotatedImage.from_grayscale(im)

The :class:`jicbioimage.illustrate.Canvas` instance has built in annotation
functionality.

One can use it to draw crosses.

>>> canvas.draw_cross(10, 20)

One can use it to mask out bitmaps (in the example below with the color cyan).

>>> bitmap = np.zeros((50, 50), dtype=bool)
>>> bitmap[30:40, 30:40] = True
>>> canvas.mask_region(bitmap, color=(0, 255, 255))

One can use it to add text at particular locations on the canvas.

>>> canvas.text_at("Hello", 30, 60)

"""

import os.path

import PIL.ImageFont
import numpy as np
import skimage.draw

import jicbioimage.core.image

__version__ = "0.6.0"

HERE = os.path.dirname(__file__)
DEFAULT_FONT_PATH = os.path.join(HERE, "fonts", "UbuntuMono-R.ttf")


class Canvas(jicbioimage.core.image._BaseImage):
    """Class for building up annotated images."""

    @staticmethod
    def blank_canvas(width, height):
        """Return a blank canvas to annotate.

        :param width: xdim (int)
        :param height: ydim (int)
        :returns: :class:`jicbioimage.illustrate.Canvas`
        """
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        return canvas.view(Canvas)

    def draw_cross(self, position, color=(255, 0, 0), radius=4):
        """Draw a cross on the canvas.

        :param position: (row, col) tuple
        :param color: RGB tuple
        :param radius: radius of the cross (int)
        """
        y, x = position
        for xmod in np.arange(-radius, radius+1, 1):
            xpos = x + xmod
            if xpos < 0:
                continue  # Negative indices will draw on the opposite side.
            if xpos >= self.shape[1]:
                continue  # Out of bounds.
            self[y, xpos] = color
        for ymod in np.arange(-radius, radius+1, 1):
            ypos = y + ymod
            if ypos < 0:
                continue  # Negative indices will draw on the opposite side.
            if ypos >= self.shape[0]:
                continue  # Out of bounds.
            self[ypos, x] = color

    def draw_line(self, pos1, pos2, color=(255, 0, 0)):
        """Draw a line between pos1 and pos2 on the canvas.

        :param pos1: position 1 (row, col) tuple
        :param pos2: position 2 (row, col) tuple
        :param color: RGB tuple
        """
        r1, c1 = tuple([int(round(i, 0)) for i in pos1])
        r2, c2 = tuple([int(round(i, 0)) for i in pos2])
        rr, cc = skimage.draw.line(r1, c1, r2, c2)
        self[rr, cc] = color

    def mask_region(self, region, color=(0, 255, 0)):
        """Mask a region with a color.

        :param region: :class:`jicbioimage.core.region.Region`
        :param color: RGB tuple
        """
        self[region] = color

    def text_at(self, text, position, color=(255, 255, 255),
                size=12, antialias=False, center=False):
        """Write text at x, y top left corner position.

        By default the x and y coordinates represent the top left hand corner
        of the text. The text can be centered vertically and horizontally by
        using setting the ``center`` option to ``True``.

        :param text: text to write
        :param position: (row, col) tuple
        :param color: RGB tuple
        :param size: font size
        :param antialias: whether or not the text should be antialiased
        :param center: whether or not the text should be centered on the
                       input coordinate
        """
        def antialias_value(value, normalisation):
            return int(round(value * normalisation))

        def antialias_rgb(color, normalisation):
            return tuple([antialias_value(v, normalisation) for v in color])

        def set_color(xpos, ypos, color):
            try:
                self[ypos, xpos] = color
            except IndexError:
                pass

        y, x = position
        font = PIL.ImageFont.truetype(DEFAULT_FONT_PATH, size=size)
        mask = font.getmask(text)
        width, height = mask.size
        if center:
            x = x - (width // 2)
            y = y - (height // 2)
        for ystep in range(height):
            for xstep in range(width):
                normalisation = mask[ystep * width + xstep] / 255.
                if antialias:
                    if normalisation != 0:
                        rgb_color = antialias_rgb(color, normalisation)
                        set_color(x + xstep, y+ystep, rgb_color)
                else:
                    if normalisation > .5:
                        set_color(x + xstep, y + ystep, color)


class AnnotatedImage(Canvas):
    """Class for building up annotated images."""

    @staticmethod
    def from_grayscale(im, channels_on=(True, True, True)):
        """Return a canvas from a grayscale image.

        :param im: single channel image
        :channels_on: channels to populate with input image
        :returns: :class:`jicbioimage.illustrate.Canvas`
        """
        xdim, ydim = im.shape
        canvas = np.zeros((xdim, ydim, 3), dtype=np.uint8)
        for i, include in enumerate(channels_on):
            if include:
                canvas[:, :, i] = im
        return canvas.view(AnnotatedImage)
