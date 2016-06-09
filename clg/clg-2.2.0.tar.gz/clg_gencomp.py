#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import sys
import clg
from collections import OrderedDict

# Command-line configuration.
OPTIONS = OrderedDict()
OPTIONS['prog'] = {'short': 'p',
                   'required': True,
                   'help': 'Program name'}
OPTIONS['conf'] = {'short': 'c',
                   'required': True,
                   'metavar': 'FILEPATH',
                   'help': 'Configuration file of the command.'}
OPTIONS['format'] = {'short': 'f',
                     'required': True,
                     'choices': ['yaml', 'json'],
                     'help': 'Format of configuration file.'}
OPTIONS['output'] = {'short': 'o',
                     'required': True,
                     'metavar': 'FILEPATH',
                     'help': 'Output file.'}
OPTIONS['ignore_opts'] = {'short': 'i',
                          'action': 'store_true',
                          'help': "When there are subcommands, don't complete "
                                  "options. With simple completion, completion "
                                  "is generate alphabetically but ignoring "
                                  "dashes of options which can generate an "
                                  '"ugly" result.'}

BASH_OPTS = OPTIONS.copy()
ZSH_OPTS = OPTIONS.copy()
ZSH_OPTS['simple'] = {'short': 's',
                      'action': 'store_true',
                      'help': "Generate completion without printing the "
                              "descriptions of options and subcommands."}

PARSERS = OrderedDict()
PARSERS['bash'] = {'options': BASH_OPTS}
PARSERS['zsh'] = {'options': ZSH_OPTS}
CMD = {'subparsers': PARSERS}


def main():
    cmd = clg.CommandLine(CMD)
    args = cmd.parse()

    if args.format == 'yaml':
        import yaml
        import yamlordereddictloader
        config = yaml.load(open(args.conf),
                           Loader=yamlordereddictloader.Loader)
    elif args.format == 'json':
        import simplejson as json
        config = json.loads(open(args.conf,
                            object_pairs_hook=OrderedDict))

    gen_cmd = clg.CommandLine(config)
    function = 'gen_%s_completion' % args.command0
    function_args = [args.prog]
    function_kwargs = {'ignore_opts': args.ignore_opts}
    if args.command0 == 'zsh':
        function_kwargs['simple'] = args.simple
    completion = getattr(gen_cmd, function)(*function_args, **function_kwargs)
    print(completion)

    with open(args.output, 'w') as fhandler:
        fhandler.write(completion)


if __name__ == '__main__':
    main()
