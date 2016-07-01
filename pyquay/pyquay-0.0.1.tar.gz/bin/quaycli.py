#!/usr/bin/env python
import pyquay
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    catsubparsers = parser.add_subparsers(dest='category')

    securityparser = catsubparsers.add_parser(
        'security',
        help='Create a tenant or interact with tenant assets')

    add_security_actions(securityparser)

    return parser.parse_args()


def add_security_actions(parser):
    securityactsubparser = parser.add_subparsers(
        dest='action',
        metavar='(get_vulnerability_list|...)')

    getvulnparser = securityactsubparser.add_parser(
        'get_vulnerability_list',
        help='Get the vuln list for an image')
    getvulnparser.add_argument(
        '--repo',
        help='The Quay repo')
    getvulnparser.add_argument(
        '--image',
        help='The image')

    add_client_generation_args(getvulnparser)


def add_client_generation_args(parser):
    clientparser = parser.add_argument_group(
        'Client information',
        'Paramaters for creating a client.')
    clientparser.add_argument(
        '--token',
        help='The Quay API token')


def main(args):
    print dir(pyquay)
    c = pyquay.Client(args.token)

    if args.category == 'security':
        c.security(args.repo, args.image)


if __name__ == '__main__':
    args = get_args()
    main(args)
