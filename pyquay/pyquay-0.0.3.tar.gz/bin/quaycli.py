#!/usr/bin/env python
import pyquay
import argparse
import json


def get_args():
    parser = argparse.ArgumentParser()
    catsubparsers = parser.add_subparsers(dest='category')

    repoparser = catsubparsers.add_parser(
        'repository',
        help='Interact with a repository')

    add_repo_actions(repoparser)

    return parser.parse_args()


def add_repo_actions(parser):
    repoactsubparser = parser.add_subparsers(
        dest='action',
        metavar='(security|images|...)')

    getrepoparser = repoactsubparser.add_parser(
        'security',
        help='Get the vuln list for an image')
    getrepoparser.add_argument(
        '--repo',
        help='The Quay repo')
    getrepoparser.add_argument(
        '--image',
        help='The image')
    getrepoparser.add_argument(
        '--output',
        help='The output file')
    add_client_generation_args(getrepoparser)

    getrepoparser = repoactsubparser.add_parser(
        'images',
        help='Get the vuln list for an image')
    getrepoparser.add_argument(
        '--repo',
        help='The Quay repo')
    getrepoparser.add_argument(
        '--tag',
        help='The tag')

    add_client_generation_args(getrepoparser)


def add_client_generation_args(parser):
    clientparser = parser.add_argument_group(
        'Client information',
        'Paramaters for creating a client.')
    clientparser.add_argument(
        '--token',
        help='The Quay API token')


def main(args):
    c = pyquay.Client(args.token)

    if args.category == 'repository':
        if args.action == 'security':
            report = c.security(args.repo, args.image)
            with open(args.output, 'w') as f:
                f.write(json.dumps(report))
        if args.action == 'images':
            print c.get_images_by_tag(args.repo, args.tag)


if __name__ == '__main__':
    args = get_args()
    main(args)
