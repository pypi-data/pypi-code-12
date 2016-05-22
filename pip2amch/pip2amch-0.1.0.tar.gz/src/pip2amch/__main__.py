# coding: utf-8
from __future__ import division, absolute_import
from __future__ import print_function


import click
import sys
import requirements
import tablib


# Why does this file exist, and why __main__?
# For more info, read:
# - https://www.python.org/dev/peps/pep-0338/
# - https://docs.python.org/2/using/cmdline.html#cmdoption-m
# - https://docs.python.org/3/using/cmdline.html#cmdoption-m


@click.command()
@click.option('--tag', help='How to tag all versions.')
@click.argument('filename')
def main(filename, tag):

    with open(filename) as f:
        lines = f.readlines()
        lines = (line.split('#', 1)[0] for line in lines)
        lines = (line.strip() for line in lines)
        reqs = '\n'.join(lines)

    parsed = requirements.parse(reqs)
    data = tablib.Dataset()
    data.headers = ['namespace', 'name', 'version']
    if tag:
        data.headers.append('tag')

    def extract_version(specs):
        for spec, version in specs:
            if spec == '==':
                return version
        return ''

    for item in parsed:
        item = [
            'python',
            item.name,
            extract_version(item.specs),
        ]
        if tag:
            item.append(tag)

        data.append(item)

    print(data.csv)


if __name__ == "__main__":
    sys.exit(main())
