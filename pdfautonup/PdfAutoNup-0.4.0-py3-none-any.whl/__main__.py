#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2016
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Main function for the command."""

try:
    from math import gcd
except ImportError:
    from fractions import gcd
import os
import sys

from PyPDF2.generic import NameObject, createStringObject
import PyPDF2

from pdfautonup import LOGGER
from pdfautonup import errors, options, paper, geometry

def lcm(a, b):
    """Return least common divisor of arguments"""
    # pylint: disable=invalid-name, deprecated-method
    return a * b / gcd(a, b)

def _none_function(*args, **kwargs):
    """Accept any number of arguments. and does nothing."""
    # pylint: disable=unused-argument
    pass

def _progress_printer(string):
    """Returns a function that prints the progress message."""

    def print_progress(page, total):
        """Print progress message."""
        try:
            text = string.format(
                page=page,
                total=total,
                percent=int(page*100/total),
                )
        except: # pylint: disable=bare-except
            text = string
        print(text, end="")
        sys.stdout.flush()

    return print_progress

class PageIterator:
    """Iterator over pages of several pdf documents."""
    # pylint: disable=too-few-public-methods

    def __init__(self, files):
        self.files = files

    def __iter__(self):
        for pdf in self.files:
            for num in range(pdf.numPages):
                yield pdf.getPage(num)

    def __len__(self):
        return sum([pdf.numPages for pdf in self.files])

    def repeat_iterator(self, num):
        """Iterator over pages, repeated ``num`` times."""
        for __ignored in range(int(num)):
            yield from self

def _aggregate_metadata(files):
    """Aggregate metadata from input files."""
    input_info = [file.getDocumentInfo() for file in files]
    output_info = PyPDF2.pdf.DocumentInformation()

    if len(files) == 1:
        return input_info[0]

    for key in ["/Title", "/Author", "/Keywords", "/Creator", "/Subject"]:
        values = set([
            data[key]
            for data
            in input_info
            if (key in data and data[key])
            ])
        if len(values):
            value = ', '.join(['“{}”'.format(item) for item in values])
            if len(values) != len(files):
                value += ", and maybe others."
            output_info[NameObject(key)] = createStringObject(value)
    return output_info

def rectangle_size(rectangle):
    """Return the dimension of rectangle (width, height)."""
    return (
        rectangle.upperRight[0] - rectangle.lowerLeft[0],
        rectangle.upperRight[1] - rectangle.lowerLeft[1],
        )

def add_extension(filename):
    """Return the argument, with the `.pdf` extension if missing.

    If `filename` does not exist, but `filename.pdf` does exist, return the
    latter. Otherwise (even if it does not exist), return the former.
    """
    if not os.path.exists(filename):
        extended = "{}.pdf".format(filename)
        if os.path.exists(extended):
            return extended
    return filename

def nup(arguments, progress=_none_function):
    """Build destination file."""
    input_files = list()
    for pdf in arguments.files:
        try:
            input_files.append(PyPDF2.PdfFileReader(add_extension(pdf)))
        except (FileNotFoundError, PyPDF2.utils.PdfReadError, PermissionError) as error:
            raise errors.InputFileError(pdf, error)

    pages = PageIterator(input_files)

    page_sizes = list(zip(*[rectangle_size(page.mediaBox) for page in pages]))
    source_size = (max(page_sizes[0]), max(page_sizes[1]))
    target_size = paper.target_papersize(arguments.target_size)

    if arguments.algorithm is None:
        if arguments.gap[0] is None and arguments.margin[0] is None:
            fit = geometry.Fuzzy
        else:
            fit = geometry.Panelize
    else:
        fit = {
            'fuzzy': geometry.Fuzzy,
            'panel': geometry.Panelize,
            }[arguments.algorithm]

    dest = fit(
        source_size,
        target_size,
        arguments=arguments,
        metadata=_aggregate_metadata(input_files),
        )

    if arguments.repeat == 'auto':
        if len(pages) == 1:
            arguments.repeat = 'fit'
        else:
            arguments.repeat = 1 # pylint: disable=redefined-variable-type
    if isinstance(arguments.repeat, int):
        repeat = arguments.repeat
    elif arguments.repeat == 'fit':
        repeat = lcm(dest.pages_per_page, len(pages)) // len(pages)

    pagecount = 0
    pagetotal = int(repeat * len(pages))
    progress(pagecount, pagetotal)
    for page in pages.repeat_iterator(repeat):
        dest.add_page(page)
        pagecount += 1
        progress(pagecount, pagetotal)

    dest.write(options.destination_name(arguments.output, add_extension(arguments.files[0])))

def main():
    """Main function"""
    arguments = options.commandline_parser().parse_args(sys.argv[1:])

    try:
        nup(arguments, progress=_progress_printer(arguments.progress))
        if not (arguments.progress.endswith("\n") or arguments.progress == ""):
            print()
    except KeyboardInterrupt:
        print()
        sys.exit(1)
    except errors.PdfAutoNupError as error:
        LOGGER.error(error)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
