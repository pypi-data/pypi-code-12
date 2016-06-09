import argparse
import os
import sys

from cratis.add import add_cmd
from cratis.bootstrap import init_app
# from cratis.env import install_feature_dependencies


def django_cmd():
    """
    Command that executes django ./manage.py task + loads environment variables from cratis.yml

    Command also can be executed from sub-folders of project.
    """
    os.system('.pyvenv/bin/django-manage %s' % (' '.join(sys.argv[1:])))

    print()


def cratis_cmd():
    """

    """
    print("""
┌─┐┬─┐┌─┐┌┬┐┬┌─┐
│  ├┬┘├─┤ │ │└─┐
└─┘┴└─┴ ┴ ┴ ┴└─┘
""")

    parser = argparse.ArgumentParser(prog='cratis')

    subparsers = parser.add_subparsers()

    # install_subparser = subparsers.add_parser('install', help='Install application dependencies')
    # install_subparser.add_argument("--env", type=str, help="Settings Class (Environment)", default="Dev", nargs='?')
    # install_subparser.add_argument("--dump", action="store_true", default=False, help="Only dump, do not install")
    # install_subparser.add_argument("--upgrade", action="store_true", default=False, help="Update dependencies")
    # install_subparser.set_defaults(func=install_feature_dependencies)

    init_subparser = subparsers.add_parser('init', help='Create empty settings file')
    init_subparser.add_argument("--cratis-path", '--cp', help="Local cratis directory to install with -e attribute")
    init_subparser.set_defaults(func=init_app)

    init_subparser = subparsers.add_parser('add', help='Install feature from github')
    init_subparser.add_argument("url", help="Feature url in format [(ssh|https)://][admin][.][@django-cratis][/cratis-admin][#master]")
    init_subparser.set_defaults(func=add_cmd)

    if len(sys.argv) < 2:
        parser.print_help()
        print()
        return

    args = parser.parse_args(sys.argv[1:])

    if args.func:
        args.func(**vars(args))
        print()
    else:
        parser.print_help()
        print()

