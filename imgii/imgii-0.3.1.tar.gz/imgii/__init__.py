#!/usr/bin/env python3

# Written by Gem Newman. This work is licensed under the MPL2 License.


import requests
from shutil import get_terminal_size
from argparse import ArgumentParser
from PIL import Image
from colorama import Fore


CHARS = ' .-=;+*#@%'
BLOCKS = ' ░▒▓█'
DEFAULT_SCALE = 2
DEFAULT_PIXELS_PER_CHAR = 8

# Larger values bias toward white/grey, smaller toward more colour.
PRIMACY_DIFF = 0.15
COLOR_MAP = {
    (0, 0, 0): Fore.BLACK,
    (1, 0, 0): Fore.RED,
    (0, 1, 0): Fore.GREEN,
    (0, 0, 1): Fore.BLUE,
    (1, 1, 0): Fore.YELLOW,
    (1, 0, 1): Fore.MAGENTA,
    (0, 1, 1): Fore.CYAN,
    (1, 1, 1): Fore.WHITE,
}


def image_to_ascii(
    image_file, output_width=None, console_width=None, scale=DEFAULT_SCALE,
    invert=False, url=False, chars=CHARS, color=False
):
    n_chars = len(chars)

    # Try to guess if the file is a URL, in case the user was just lazy.
    url = url or image_file.startswith(('http://', 'https://'))

    if url:
        r = requests.get(image_file, stream=True)
        r.raw.decode_content = True    # Handles spurious content encoding.
        image_file = r.raw

    # Load the image into Pillow, scale appropriately, convert to greyscale.
    with Image.open(image_file) as image:
        x, y = image.size
        dims = output_dimensions(x, y, scale, output_width, console_width)
        image = image.resize(dims)

        # Get greyscale pixel values.
        pixels = image.convert('L').getdata()

        if color:
            colors = list(map(ansi_color, image.convert('RGB').getdata()))

    text = []

    # Assign a character to represent each pixel.
    for i, pixel in enumerate(pixels):
        if (i > 0) and (i % dims[0] == 0):
            text.append('\n')

        index = int(pixel * n_chars / 256)

        if color and (i == 0 or colors[i - 1] != colors[i]):
            text.append(colors[i])

        text.append(chars[index if not invert else n_chars - 1 - index])

    if color: text.append(Fore.RESET)

    return ''.join(text)


def output_dimensions(x, y, scale, output_width=None, console_width=None):
    if not output_width:
        if not console_width:
            console_width = get_terminal_size()[0]
        output_width = max(min(x // DEFAULT_PIXELS_PER_CHAR, console_width), 1)

    output_height = max(int(y * output_width / (x * scale)), 1)

    return (output_width, output_height)


# Could perhaps be improved by using a blend of fore/back for ranges that fall
# between the available ANSI colours.
def ansi_color(rgb):
    # Scale and round to determine which colours are primarily involved.
    if max(rgb) > 0:
        rgb = [x / max(rgb) for x in rgb]
    else:
        rgb = list(rgb)

    # Order colour indices by importance ([0, 2, 1] would mean red is primary).
    primacy = sorted(range(len(rgb)), key=lambda k: rgb[k], reverse=True)
    has_secondary = rgb[primacy[1]] >= 1 - PRIMACY_DIFF
    has_tertiary = rgb[primacy[2]] >= rgb[primacy[1]] - PRIMACY_DIFF

    rgb[primacy[0]] = 1
    rgb[primacy[1]] = int(has_secondary)
    rgb[primacy[2]] = int(has_secondary and has_tertiary)

    return COLOR_MAP[tuple(rgb)]


def main():
    parser = ArgumentParser(description='Converts images to ASCII.')
    parser.add_argument('image', help='The filename or URL of the image.')
    parser.add_argument('-s', '--vertical-scale', help='The factor to use when'
                        ' scaling to account for rectangular ASCII characters.'
                        ' Defaults to {}.'.format(DEFAULT_SCALE), type=float,
                        default=DEFAULT_SCALE)
    parser.add_argument('-u', '--url', help='Interpret IMAGE as a URL instead '
                        'of as a local file. (If this flag is omitted, imgii '
                        'will attempt to guess.)', action='store_true')
    parser.add_argument('-i', '--invert', help='Invert dark/light portions of '
                        'the image (for viewing on light backgrounds).',
                        action='store_true')
    parser.add_argument('-c', '--color', help='Use ANSI colors.',
                        action='store_true')
    width_group = parser.add_mutually_exclusive_group()
    width_group.add_argument('-w', '--output-width', help='The output width, '
                             'in characters. If not specified, imgii will '
                             'attempt to guess based on image and console '
                             'dimensions.', type=int, default=None)
    width_group.add_argument('-d', '--console-width', help='The console width '
                             'to use when guessing output dimensions. Defaults'
                             ' to actual console width.', type=int,
                             default=None)
    char_group = parser.add_mutually_exclusive_group()
    char_group.add_argument('-a', '--chars', help='The character set to use, '
                            'from darkest to lightest. Default: {}%'
                            .format(CHARS), default=CHARS)
    char_group.add_argument('-b', '--blocks', help='Use the following Unicode '
                            'block elements: {}'.format(BLOCKS),
                            action='store_true')
    args = parser.parse_args()

    print(
        image_to_ascii(
            args.image, args.output_width, args.console_width,
            args.vertical_scale, args.invert, args.url,
            args.chars if not args.blocks else BLOCKS, args.color
        )
    )


if __name__ == '__main__':
    main()
