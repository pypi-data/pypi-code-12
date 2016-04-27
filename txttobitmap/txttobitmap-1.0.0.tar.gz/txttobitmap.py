#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from math import ceil, sqrt

from PIL import Image

MODES = ('palette', 'grayscale')

PALETTE = [
    0x000000,  # 0 — black
    0x000080,  # 1 — maroon
    0x008000,  # 2 — green
    0x008080,  # 3 — olive
    0x800000,  # 4 — navy
    0x800080,  # 5 — purple
    0x808000,  # 6 — teal
    0xc0c0c0,  # 7 — silver
    0x808080,  # 8 — gray
    0x0000ff,  # 9 — red
    0x00ff00,  # 10 — lime
    0x00ffff,  # 11 — yellow
    0xff0000,  # 12 — blue
    0xff00ff,  # 13 — fuchsia
    0xffff00,  # 14 — aqua
    0xffffff  # 15 — white
]


def create_parser():
    """Create application argument parser."""
    parser = argparse.ArgumentParser(
        description='Convert given file to a bitmap.')
    parser.add_argument('input', help='a file to convert')
    parser.add_argument('output', help='path to the file to save')
    parser.add_argument(
        '-m, --mode', default='palette', choices=MODES, dest='mode',
        help='converting mode. One of: "palette" (each byte converted to two '
             'pixels using 16-color palette, default), "grayscale" (each byte '
             'value represented as grayscale)')
    return parser


def convert(data, mode):
    """Convert given file to bitmap.

    :param bytes data: input data to convert to a bitmap
    :param str mode: one of the values:
    * palette - represent each byte as two pixels using 16-color palette
    * grayscale - represent each byte as one grayscale pixel using its value
    :return: result image
    :rtype: Image.Image
    """
    if mode not in MODES:
        raise ValueError('mode not one of the values: {}'.format(MODES))

    length = len(data)
    if mode == 'palette':
        length *= 2
    img_mode = 'L' if mode == 'grayscale' else 'RGB'

    size = int(ceil(sqrt(length)))
    img = Image.new(img_mode, (size, size))
    for i in range(len(data)):
        if mode == 'grayscale':
            add_pixel(img, i, size, data[i])
        elif mode == 'palette':
            add_pixel(img, i * 2, size, PALETTE[data[i] // 16])
            add_pixel(img, i * 2 + 1, size, PALETTE[data[i] % 16])

    return img


def add_pixel(img, index, size, pixel):
    """Add a pixel to the image at (index % size, index / size).

    :param Image.Image img: image to alter
    :param int index: index of the byte
    :param int size: width of the image
    :param int pixel: pixel value to set
    """
    img.putpixel((index % size, index // size), pixel)


def main():
    args = create_parser().parse_args()
    data = open(args.input, 'rb').read()
    convert(data, args.mode).save(args.output)


if __name__ == '__main__':
    main()
