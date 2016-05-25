#!/usr/bin/env python3

from . import MetaExtractor, Message, HEADER_TEMPLATE
import argparse
import importlib
import time


def main():
    """
    Extract translatable strings from given input files.
    """

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('input_files', metavar='INPUTFILE', nargs='+',
                        help='input templates or python files')

    parser.add_argument('-f', '--files-from', dest='input_files', metavar='FILE',
                        action='append',
                        help='get list of input files from FILE')

    parser.add_argument('-d', '--default-domain', dest='domain', metavar='NAME',
                        action='store', default='messages',
                        help='use NAME.po for output instead of messages')

    parser.add_argument('-o', '--output', dest='output_file', metavar='FILE',
                        action='store',
                        help='write output to specified file')

    parser.add_argument('--from-code', dest='charset', metavar='NAME',
                        action='store', default="ASCII",
                        help='encoding of input files '
                             'By default the input files are '
                             'assumed to be in {default}.')

    parser.add_argument('-F', '--sort-by-file', dest='sort_output',
                        action='store_true',
                        help='sort output by file location')

    parser.add_argument('--copyright-holder', dest='copyright_holder',
                        action='store', default="THE PACKAGE'S COPYRIGHT HOLDER",
                        help='set copyright holder in output')

    parser.add_argument('--package-name', dest='package_name', metavar="PACKAGE",
                        action='store',
                        help='set package name in output')

    parser.add_argument('--package-version', dest='package_version', metavar="VERSION",
                        action='store',
                        help='set package name in output')

    parser.add_argument('--msgid-bugs-address', dest='bugs_address', metavar="EMAIL@ADDRESS",
                        action='store', default='',
                        help='set report address for msgid bugs')

    parser.add_argument('--module', dest='extractor_module', metavar="PYTHON_MODULE",
                        action='store',
                        help='python module name to extend pywebgettext')

    args = parser.parse_args()
    if args.output_file is None:
        args.output_file = '{}.po'.format(args.domain)

    if args.package_name is not None:
        args.package = args.package_name
        if args.package_version is not None:
            args.package = " " + args.package_version
    else:
        args.package = 'PACKAGE VERSION'

    if args.extractor_module is not None:
        importlib.import_module(args.extractor_module)

    messages_by_msgid = dict()
    for file_name in args.input_files:
        for extractor in MetaExtractor.extractors.values():
            if extractor().extract(messages_by_msgid, file_name):
                break

    messages = list(messages_by_msgid.values())
    if args.sort_output:
        for message in messages:
            message.references.sort()
        messages.sort(key=lambda msg: msg.references)

    with open(args.output_file, 'w') as output_file:
        headers = HEADER_TEMPLATE.format(
            time=time.strftime('%Y-%m-%d %H:%M%z'),
            args=args
        )
        output_file.write(headers)
        for message in messages:
            output_file.write('{}\n'.format(message))


if __name__ == '__main__':
    main()
