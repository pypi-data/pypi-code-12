#!/usr/bin/env python3
"""
Print the number of characters in a string.
"""
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def add_arguments(parser):
	arg = parser.add_argument
	arg('string', help='The string')


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()

	print(len(args.string))


if __name__ == '__main__':
	main()
