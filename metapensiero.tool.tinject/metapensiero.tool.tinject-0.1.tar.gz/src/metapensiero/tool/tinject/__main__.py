# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Main CLI
# :Created:   gio 21 apr 2016 18:18:46 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sys
from traceback import print_exc

from yaml import YAMLError

from .action import Action
from .state import State


OK, SOFTWARE, USAGE, DATAERR, USERBREAK, CONFIG = 0, 1, 2, 3, 4, 128


def do_apply(args):
    "Execute one or more actions"

    try:
        state = State(args.verbose, args.dry_run, args.overwrite, args.config)
    except YAMLError as e:
        print("YAML error: %s" % e)
        return CONFIG

    for name in args.action:
        if name not in state.config.actions:
            print('Unrecognized action name: %s' % name)
            return DATAERR
    state()
    for name in args.action:
        Action(state, name, state.config.actions[name])()
    return OK


def do_list(args):
    "List available actions"

    print("Available actions:")
    state = State(args.verbose, args.dry_run, args.overwrite, args.config)
    for name in state.config.actions:
        action = Action(state, name, state.config.actions[name])
        print('\n%s\n\t%s' % (name, action.description))
    return OK


def do_fold(args):
    "Fold the configuration into a self contained single YAML file"

    state = State(args.verbose, args.dry_run, args.overwrite, args.config)
    state.config.write(args.output)
    return OK


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import locale

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(description="Template injecter",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help="emit traceback on error")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="emit some noise in the process")
    parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                        help="test run, just show what would happed")
    parser.add_argument('-o', '--overwrite', action='store_true', default=False,
                        help="whether existing files shall be overwritten")

    subparsers = parser.add_subparsers()

    subp = subparsers.add_parser('apply', help=do_apply.__doc__)
    subp.add_argument('config', help="YAML configuration")
    subp.add_argument('action', nargs='+', help="Action to be performed")
    subp.set_defaults(func=do_apply)

    subp = subparsers.add_parser('list', help=do_list.__doc__)
    subp.add_argument('config', help="YAML configuration")
    subp.set_defaults(func=do_list)

    subp = subparsers.add_parser('fold', help=do_fold.__doc__)
    subp.add_argument('config', help="YAML configuration")
    subp.add_argument('output', help="Output file name")
    subp.set_defaults(func=do_fold)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        try:
            return args.func(args)
        except Exception as e:
            print('Error: %s' % e)
            if args.debug:
                print_exc()
            return SOFTWARE
        except KeyboardInterrupt:
            return USERBREAK
    else:
        return OK


if __name__ == '__main__':
    sys.exit(main())
