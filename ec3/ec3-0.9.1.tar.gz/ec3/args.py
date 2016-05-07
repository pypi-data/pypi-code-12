#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from collections import namedtuple
import argparse
from ec3 import exceptions

def parse_tag_filters(tag_str):
    tags = {}
    if tag_str:
        if ',' in tag_str:
            pieces = tag_str.split(',')
        else:
            pieces = [tag_str]

        for piece in pieces:
            failed_to_split = False
            try:
                key, val = piece.split('=')
            except ValueError:
                failed_to_split = True

            if failed_to_split or (not val):
                raise exceptions.InvalidInput(
                    tag_str,
                    "tag filters should be formatted as: 'key1=val1,key2=val2"
                )
            key = key.strip()
            val = val.strip()
            tags[key] = val
    return tags


ParsedArgs = namedtuple('ParsedArgs', [
    'tags', 'command', 'vpc_scope', 'escape_env', 'user', 'key_file_path'
])


HELP="""

SSH into ec2 instances.


To filter by VPC:
        export EC3_VPC_SCOPE=vpc-id-41245
    or pass:
        ec3 --vpc vpc-id-41245


To specify user:
        export EC3_REMOTE_USER=username
    or pass:
        ec3 -u username


To specify an SSH key:
        export EC3_KEY_FILE_PATH="/home/you/.ssh/id_rsa"
    or pass:
        ec3 -i /home/you/.ssh/id_rsa


To filter by instance tags:
        export EC3_TAG_FILTERS=key1:val1,key2:val2
    or pass:
        ec3 --tags key1:val1 key2:val2 key3:val3
    Note that tag filters passed on the command line are
    *combined with* any tags specified by environment
    variable.


"""

def make_parser():
    parser = argparse.ArgumentParser(
        description=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'command', help='command {ssh, shell}'
    )
    parser.add_argument(
        '--tags', action='append', nargs='*',
        help='additional tag filters, formatted as "key1=val1 key2=val2"')

    parser.add_argument('--vpc', dest='vpc_scope',
                        default='', help='vpc id')

    parser.add_argument('--escape-env', metavar='escape_env', type=bool,
                        default=False,
                        help='disable existing filters from environment variables')

    parser.add_argument('-i', dest='key_file_path', type=str,
                        default='',
                        help='file path of SSH key')

    parser.add_argument('-u', dest='user', type=str,
                        default='',
                        help='remote username')
    return parser


def get_args():
    parser = make_parser()
    args = parser.parse_args()
    tags = {}
    if args.tags is None:
        args.tags = [[]]
    for key_val in args.tags[0]:
        tags.update(parse_tag_filters(key_val))
    return ParsedArgs(
        command=args.command,
        vpc_scope=args.vpc_scope,
        escape_env=args.escape_env,
        user=args.user,
        tags=tags,
        key_file_path=args.key_file_path
    )
