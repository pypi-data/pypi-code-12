#!/usr/bin/env python

import argparse
import os
import sys
import platform

from .pyalot import pyalot, PyalotError

DEFAULT_TOKEN_PATH = '~/.pushalot-token'

def main():
    try:
        parser = argparse.ArgumentParser(
            description='Send push notifications using pushalot.com')

        parser.add_argument('--title',
                help='set notification title')
        parser.add_argument('--link',
                help='add link to notification')
        parser.add_argument('--link-title',
                help='set link title (ignored if --link not used)')
        parser.add_argument('--source', default=platform.node(),
                help='set notification source, default: hostname')
        parser.add_argument('--image',
                help='set notification image url')
        parser.add_argument('--ttl', type=int,
                help='set notification timeout in minutes')
        parser.add_argument('--silent', action='store_true',
                help='mark notification as silent')
        parser.add_argument('--important', action='store_true',
                help='mark notification as important')
        parser.add_argument('--token',
                help='specify pushalot.com auth token')
        parser.add_argument('--token-path', default=DEFAULT_TOKEN_PATH,
                help='specify pushalot.com token file path; defaults to %s; '
                    'ignored if --token is used' % DEFAULT_TOKEN_PATH)
        parser.add_argument('--pipe', action='store_true',
                help='read notification text from stdin')
        parser.add_argument('body', nargs='*',
                help='notification text; ignored if --pipe used')

        args = parser.parse_args()

        if args.token:
            token = args.token
        else:
            try:
                with open(os.path.expanduser(args.token_path)) as f:
                    token = f.read().strip()
            except Exception as e:
                print 'Error loading token:', e
                return 1

        if args.pipe:
            # read body from stdin
            body = '\n'.join(line for line in sys.stdin)
        else:
            # read body from arguments
            body = ' '.join(args.body)

        try:
            pyalot(body=body,
                    title=args.title, source=args.source,
                    link=args.link, link_title=args.link_title,
                    image=args.image,
                    silent=args.silent, important=args.important,
                    ttl=args.ttl,
                    token=token)
        except PyalotError as e:
            print e
            return 1

    except KeyboardInterrupt:
        return 1


if __name__ == '__main__':
    main()
