from __future__ import absolute_import

import argparse
import logging

from .mirror import PypiMirror

logging.basicConfig(level=logging.INFO)
           
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('mirror_root', help='Where to clone pypi locally')
    parser.add_argument('--mirror', '-m', default='https://pypi.python.org/simple', help='Python mirror to clone from.  The default is https://pypi.python.org/simple')
    parser.add_argument('--verify-ssl', '-v', default=True, action='store_true', help='Whether to validate SSL Certs')
    parser.add_argument('--timeout', '-t', default=None, help='Requests timeout')
    parser.add_argument('--workers', '-w', default=3, help='Number of threads to use to mirror. Default is 3.')

    args = parser.parse_args()

    pm = PypiMirror(args.mirror_root, pypi_mirror_url=args.mirror, verify=args.verify_ssl, timeout=args.timeout, workers=args.workers)
    pm.get_simple_listing()

if __name__ == '__main__':
    main()
