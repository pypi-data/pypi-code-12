# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

import six

if six.PY2:
    # to evade UnicodeDecodeError on plistlib.writePlist
    reload(sys)
    sys.setdefaultencoding('utf-8')

import argparse
import shutil
import os.path

from yamlfred.utils import TemporaryDirectory

from yamlfred.alfred_workflow import AlfredWorkflow

__version__ = '0.3.3'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="A tool to manage Alfred Workflow via yaml templates",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(help='commands')

    plist_parser = subparsers.add_parser(
        'to_yaml', help='convert plist into workflow.yml'
    )
    plist_parser.set_defaults(func=to_yaml)

    yaml_parser = subparsers.add_parser(
        'to_plist', help='convert yaml templates into info.plist'
    )
    yaml_parser.set_defaults(func=to_plist)

    extract_parser = subparsers.add_parser(
        'extract', help='extract Alfred workflow'
    )
    extract_parser.add_argument(
        'path', action='store', help='path to Alfred workflow'
    )
    extract_parser.set_defaults(func=extract)

    version_parser = subparsers.add_parser(
        'version', help='show version'
    )
    version_parser.set_defaults(func=lambda _: print(__version__))

    create_parser = subparsers.add_parser(
        'create', help='create Alfred workflow from workflow.yml'
    )
    create_parser.add_argument(
        'name', action='store', help='name of Alfred workflow'
    )
    create_parser.set_defaults(func=create)
    return parser.parse_args()


def to_yaml(args):
    wf = AlfredWorkflow()
    wf.load_plist('info.plist')
    wf.dump_workflow()
    return


def to_plist(args):
    wf = AlfredWorkflow()
    wf.load_yaml('workflow.yml')
    wf.dump_plist()
    return


def extract(args):
    import zipfile
    with zipfile.ZipFile(args.path, "r", zipfile.ZIP_DEFLATED) as zip:
        extract_path = os.path.splitext(args.path)[0]
        zip.extractall(path=extract_path)
    return


def create(args):
    wf = AlfredWorkflow()
    wf.load_yaml('workflow.yml')
    wf.dump_plist()
    # copy to tmpdir
    with TemporaryDirectory() as tmpdir:
        tmppath = os.path.join(tmpdir, args.name)
        shutil.copytree(os.path.curdir, tmppath)
        name = shutil.make_archive(args.name, 'zip', tmppath)
        shutil.move('{}.zip'.format(args.name),
                    '{}.alfredworkflow'.format(args.name))
    return


def main():
    args = parse_arguments()
    args.func(args)
    sys.exit(0)
