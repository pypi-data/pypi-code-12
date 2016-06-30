# vim: set et nosi ai ts=4 sts=4 sw=4 colorcolumn=80:
# coding: utf-8
"""
Simplified wrapper around the Pillow library.
"""

from PIL import Image as PILImage

__all__ = ['Image', 'ImageModeError', 'Pixel']


class ImageModeError(AttributeError):
    pass


class Pixel:
    """An individual pixel in an image."""

    __slots__ = ('_coords', '_mode', '_pixels', '_x', '_y')

    def __init__(self, mode, pixels, x, y, check=True):
        self._mode = mode
        self._pixels = pixels
        if check:
            # Use the property which checks the coordinates completely.
            self.coords = (x, y)
        else:
            self._x = x
            self._y = y
            self._coords = (x, y)

    def get_coords(self):
        return self._coords

    def set_coords(self, value):
        if len(value) != 2 and type(value) in (list, tuple):
            raise TypeError('The coordinates must be a pair of numbers.')
        try:
            self._pixels[value[0], value[1]]
        except TypeError:
            raise TypeError(
                    'Each coordinate must be an int or float.') from None
        except IndexError:
            try:
                self._pixels[value[0], 0]
            except IndexError:
                if value[0] < 0:
                    raise ValueError(
                        'The x-coordinate cannot be less than zero.') from None
                else:
                    raise ValueError(
                        'The x-coordinate must be less than the image width.'
                        ) from None
            if value[1] < 0:
                raise ValueError(
                    'The y-coordinate cannot be less than zero.') from None
            else:
                raise ValueError(
                    'The y-coordinate must be less than the image width.'
                    ) from None

        self._x = int(value[0])
        self._y = int(value[1])
        self._coords = (self._x, self._y)

    coords = property(get_coords, set_coords,
                      None, 'The (x, y) coordinates of the pixel.')

    def get_x(self):
        return self._x

    def set_x(self, value):
        try:
            self._pixels[value, self._y]
        except TypeError:
            raise TypeError(
                'The x-coordinate must be an int or float.') from None
        except IndexError:
            if value < 0:
                raise IndexError(
                    'The x-coordinate cannot be less than zero.') from None
            else:
                raise IndexError(
                    'The x-coordinate must be less than the image width.'
                    ) from None
        self._x = int(value)
        self._coords = (self._x, self._y)

    x = property(get_x, set_x, None, 'The x-coordinate of the pixel.')

    def get_y(self):
        return self._y

    def set_y(self, value):
        try:
            self._pixels[self._x, value]
        except TypeError:
            raise TypeError(
                'The y-coordinate must be an int or float.') from None
        except IndexError:
            if value < 0:
                raise IndexError(
                    'The y-coordinate cannot be less than zero.') from None
            else:
                raise IndexError(
                    'The y-coordinate must be less than the image height.'
                    ) from None
        self._y = int(value)
        self._coords = (self._x, self._y)

    y = property(get_y, set_y, None, 'The y-coordinate of the pixel.')

    def get_color(self):
        return self._pixels[self._coords]

    def set_color(self, value):
        if type(value) == tuple:
            if 'L' in self._mode:
                raise ImageModeError(
                    'A color tuple cannot be set on a grayscale image.')
            try:
                value = (
                    int(ch) if 0 <= ch <= 255
                    else (0 if ch < 0 else 255) for ch in value)
                self._pixels[self._coords] = value
            except (TypeError, ValueError) as e:
                if self._mode == 'RGB':
                    raise e.__class__(
                        'Color tuple must be 3 numbers.') from None
                else:
                    raise e.__class__(
                        'Color tuple must be 4 numbers.') from None
        else:
            if 'L' in self._mode:
                raise ImageModeError(
                    'A single value cannot be set on a color image.')
            try:
                value = (
                    int(value) if 0 <= value <= 255
                    else (0 if value < 0 else 255))
                self._pixels[self._coords] = value
            except TypeError:
                raise TypeError('Color must be a single number.') from None

    color = property(
        get_color, set_color, None,
        'The color value of the pixel for L, RGB, and RGBA images.')

    def get_red(self):
        if 'R' not in self._mode:
            raise ImageModeError('The image does not have a red channel.')
        return self._pixels[self._coords][0]

    def set_red(self, value):
        if 'R' not in self._mode:
            raise ImageModeError('The image does not have a red channel.')
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (value, old[1], old[2])
        except TypeError:
            raise TypeError('Red value must be a number.') from None

    red = property(
        get_red, set_red, None,
        'The red value of the pixel for RGB and RGBA images.')

    def get_green(self):
        if 'G' not in self._mode:
            raise ImageModeError('The image does not have a green channel.')
        return self._pixels[self._coords][1]

    def set_green(self, value):
        if 'G' not in self._mode:
            raise ImageModeError('The image does not have a green channel.')
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (old[0], value, old[2])
        except TypeError:
            raise TypeError('Green value must be a number.') from None

    green = property(
        get_green, set_green, None,
        'The green value of the pixel for RGB and RGBA images.')

    def get_blue(self):
        if 'B' not in self._mode:
            raise ImageModeError('The image does not have a blue channel.')
        return self._pixels[self._coords][2]

    def set_blue(self, value):
        if 'G' not in self._mode:
            raise ImageModeError('The image does not have a blue channel.')
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (old[0], old[1], value)
        except TypeError:
            raise TypeError('Blue value must be a number.') from None

    blue = property(
        get_blue, set_blue, None,
        'The blue value of the pixel for RGB and RGBA images.')

    def get_gray(self):
        if 'L' not in self._mode:
            raise ImageModeError('The image does not have a gray channel.')
        return self._pixels[self._coords]

    def set_gray(self, value):
        if 'L' not in self._mode:
            raise ImageModeError('The image does not have a gray channel.')

        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = value
        except TypeError:
            raise TypeError('Gray value must be a number.') from None

    gray = property(
        get_gray, set_gray, None,
        'The brightness value (luminosity) for grayscale (mode L) images.')
    grey = gray

    def get_alpha(self):
        if 'A' not in self._mode:
            raise ImageModeError(
                'The image does not have an alpha (opacity) channel.')
        return self._pixels[self._coords][0]

    def set_alpha(self, value):
        if 'A' not in self._mode:
            raise ImageModeError(
                'The image does not have an alpha (opacity) channel.')
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (value, old[1], old[2])
        except TypeError:
            raise TypeError(
                'Alpha (opacity) value must be a number.') from None

    alpha = property(
        get_alpha, set_alpha, None,
        'The alpha (opacity) value of the pixel for RGBA images.')
    opacity = alpha


class GrayPixel(Pixel):
    def get_color(self):
        return self._pixels[self._coords]

    def set_color(self, value):
        if type(value) == tuple:
            raise ImageModeError(
                'A color tuple cannot be set on a grayscale image.')
        else:
            try:
                value = (
                    int(value) if 0 <= value <= 255
                    else (0 if value < 0 else 255))
                self._pixels[self._coords] = value
            except TypeError:
                raise TypeError(
                    'Color must be a number on a grayscale image.') from None

    color = property(
        get_color, set_color, None,
        'The color value of the pixel for L, RGB, and RGBA images.')

    def get_gray(self):
        return self._pixels[self._coords]

    def set_gray(self, value):
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = value
        except TypeError:
            raise TypeError('Gray value must be a number.') from None

    gray = property(
        Pixel.get_gray, set_gray, None,
        'The brightness value (luminosity) for grayscale (mode L) images.')
    grey = gray


class RGBPixel(Pixel):
    def set_color(self, value):
        if type(value) == tuple:
            try:
                value = (
                    int(ch) if 0 <= ch <= 255
                    else (0 if ch < 0 else 255) for ch in value)
                self._pixels[self._coords] = value
            except (TypeError, ValueError) as e:
                if self._mode == 'RGB':
                    raise e.__class__(
                        'Color tuple must be 3 numbers.') from None
                else:
                    raise e.__class__(
                        'Color tuple must be 4 numbers.') from None
        else:
            raise ImageModeError(
                'A single value cannot be set on a color image.')

    color = property(
        Pixel.get_color, set_color, None,
        'The color value of the pixel for RGB and RGBA images.')

    def get_red(self):
        return self._pixels[self._coords][0]

    def set_red(self, value):
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (value, old[1], old[2])
        except TypeError:
            raise TypeError('Red value must be a number.') from None

    red = property(
        get_red, set_red, None,
        'The red value of the pixel for RGB and RGBA images.')

    def get_green(self):
        return self._pixels[self._coords][1]

    def set_green(self, value):
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (old[0], value, old[2])
        except TypeError:
            raise TypeError('Green value must be a number.') from None

    green = property(
        get_green, set_green, None,
        'The green value of the pixel for RGB and RGBA images.')

    def get_blue(self):
        return self._pixels[self._coords][2]

    def set_blue(self, value):
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (old[0], old[1], value)
        except TypeError:
            raise TypeError('Blue value must be a number.') from None

    blue = property(
        get_blue, set_blue, None,
        'The blue value of the pixel for RGB and RGBA images.')


class RGBAPixel(RGBPixel):
    def get_alpha(self):
        return self._pixels[self._coords][0]

    def set_alpha(self, value):
        old = self._pixels[self._coords]
        try:
            value = (
                int(value) if 0 <= value <= 255 else (0 if value < 0 else 255))
            self._pixels[self._coords] = (value, old[1], old[2])
        except TypeError:
            raise TypeError(
                'Alpha (opacity) value must be a number.') from None

    alpha = property(
        get_alpha, set_alpha, None,
        'The alpha (opacity) value of the pixel for RGBA images.')
    opacity = alpha


class Image:
    @staticmethod
    def open(filename, **kwargs):
        if not filename:
            raise ValueError('Cannot open image with empty file name.')
        return Image(PILImage.open(filename, **kwargs))

    @staticmethod
    def new(mode, width, height):
        return Image(PILImage.new(mode, (width, height)))

    @staticmethod
    def alpha_composite(image1, image2):
        return Image(PILImage.alpha_composit(image1, image2))

    @staticmethod
    def composite(image1, image2, mask):
        return Image(PILImage.composite(image1, image2, mask))

    @staticmethod
    def blend(image1, image2, alpha):
        return Image(PILImage.blend(image1, image2, alpha))

    @staticmethod
    def eval(image, *args):
        return Image(PILImage.eval(image, *args))

    @staticmethod
    def merge(*args, **kwargs):
        return Image(PILImage.merge(*args, **kwargs))

    @staticmethod
    def fromarray(*args, **kwargs):
        return Image(PILImage.fromarray(*args, **kwargs))

    @staticmethod
    def frombytes(*args, **kwargs):
        return Image(PILImage.frombytes(*args, **kwargs))

    @staticmethod
    def fromstring(*args, **kwargs):
        return Image(PILImage.fromstring(*args, **kwargs))

    @staticmethod
    def frombuffer(*args, **kwargs):
        return Image(PILImage.frombuffer(*args, **kwargs))

    def __init__(self, image):
        self._image = image
        self._pixel_access = image.load()
        self._pixel_type = {
            'L': GrayPixel,
            'RGB': RGBPixel,
            'RGBA': RGBAPixel
        }.get(self._image.mode, Pixel)

    def __getattr__(self, attr):
        # Delegate to self._image
        return getattr(self._image, attr)

    def __iter__(self):
        for x in range(self.width):
            for y in range(self.height):
                yield self._pixel_type(
                    self._image.mode, self._pixel_access, x, y, False)

    def __getitem__(self, index):
        try:
            x = index[0]
            y = index[1]
        except (TypeError, IndexError) as e:
            raise e.__class__(
                'A pixel coordinate should be a pair of numbers: (x, y).'
                ) from None
        if len(index) > 2:
            raise ValueError(
                'A pixel coordinate should be a pair of numbers: (x, y).')
        return self._pixel_type(
            self._image.mode, self._pixel_access, x, y, True)

    def save(self, filename, *args, **kwargs):
        if filename == '':
            raise ValueError('Cannot save image to empty filename.')
        return self._image.save(filename, *args, **kwargs)
