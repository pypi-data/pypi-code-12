#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imported libraries
# ----------------------------------------------------------------------------

import sys, os, pytest
import conftest

sys.path.append(os.path.abspath('.'))

from yaop import cmdline, pformat2

# Constants
# ----------------------------------------------------------------------------

params = [
	['input_file_1.dat'],
	['input_file_2.dat'],
	]
ids = ['args1', 'args2']

# Parametrized fixture
# ----------------------------------------------------------------------------

args = conftest.define_args(__file__, params, ids)

# Main function
# ----------------------------------------------------------------------------

def main_null():
	print '- entering main ...'
	print '  - global cmdline : [\n%s\n]' % pformat2(cmdline.instance)
	print '- exiting main ...'

def main_kargs(**kargs):
	print '- entering main ...'
	print '  - kargs : [\n%s\n]' % pprint.pformat(kargs)
	print '- exiting main ...'

def main_cmdline(cmdline):
	print '- entering main ...'
	print '  - cmdline : [\n%s\n]' % pformat2(cmdline)
	print '- exiting main ...'

# main = main_null
# main = main_kargs
main = main_cmdline

# Test entry point
# ----------------------------------------------------------------------------

def entry_point(args):
	# cfg = cmdline()
	# cfg = cmdline(verbose = 1)
	cfg = cmdline(verbose = 2)
	# print cfg.opts.recurse.keys()
	# pprint.pprint(cfg)
	# pprint.pprint(cfg.opts)
	# print pprint.pformat(cfg.opts.recurse.items())
	# cfg.banner()
	# cfg.usage()
	# cfg.load_cfg()
	# pprint2(cfg.opts)
	# pprint2(cfg.cfg)
	# pprint2(cfg)
	# cfg.run()
	cfg.run(args = args)

# Test function
# ----------------------------------------------------------------------------

test = conftest.define_test(entry_point)

# Application entry point
# ----------------------------------------------------------------------------

if __name__ == '__main__':
	test(sys.argv[1:])
