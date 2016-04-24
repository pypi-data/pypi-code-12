#!/usr/bin/env python3
"""
SeQuencing Tools -- command-line tools for working with sequencing data
"""
__author__ = "Marcel Martin"

import logging
import importlib
from . import HelpfulArgumentParser

from . import __version__
from .commands import fastxmod

logger = logging.getLogger(__name__)


# List of all subcommands. A module of the given name must exist and define
# add_arguments() and main() functions. Documentation is taken from the first
# line of the module’s docstring.
COMMANDS = [
	'align',
	'bam2fastq',
	'fastxmod',
	'qgramfreq',
	'chars',
	'fastagrep',
	'readcov',
	'randomseq',
	'samsetop',
	'bameof',
	'readlenhisto',
	'cutvect',
]

def main():
	logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
	parser = HelpfulArgumentParser(description=__doc__, prog='sqt')
	parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
	subparsers = parser.add_subparsers()

	for command_name in COMMANDS:
		module = importlib.import_module('.commands.' + command_name, 'sqt')
		subparser = subparsers.add_parser(command_name,
			help=module.__doc__.split('\n')[1], description=module.__doc__)
		subparser.set_defaults(func=module.main)
		module.add_arguments(subparser)

	args = parser.parse_args()
	if not hasattr(args, 'func'):
		parser.error("Please provide a command")
	else:
		args.func(args)


if __name__ == '__main__':
	main()
