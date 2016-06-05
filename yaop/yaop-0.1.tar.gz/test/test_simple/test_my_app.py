#!/usr/bin/python
# -*- coding: utf-8 -*-

"""My Application that use library 'cmdline' to automate command line options
handling and config file parsing."""

import sys, os, pytest
import conftest

# import logging
# logging.basicConfig(level = logging.DEBUG)

sys.path.append(os.path.abspath('.'))

from yaop import cmdline

# Constants
# ----------------------------------------------------------------------------

params = [
	['another modified string 1'],
	['another modified string 2'],
	]
ids = ['ams1', 'ams2']

# Parametrized fixture
# ----------------------------------------------------------------------------

args = conftest.define_args(__file__, params, ids)

# Main function
# ----------------------------------------------------------------------------

def main(cmdline):
	print '- processed command line is :'
	print cmdline

# Test entry point
# ----------------------------------------------------------------------------

def entry_point(args):
	cfg = cmdline()
	cfg.run(args = args)

# Test function
# ----------------------------------------------------------------------------

test = conftest.define_test(entry_point)

# Application entry point
# ----------------------------------------------------------------------------

if __name__ == '__main__':
	# # USAGE : not working, because sys.argv is expected to be used by cfg.run()
	# # pytest.main()
	# # pytest.main(sys.argv[1:])
	# pytest.main()
	# # pytest.main(['-s'])
	
	test(sys.argv[1:])
