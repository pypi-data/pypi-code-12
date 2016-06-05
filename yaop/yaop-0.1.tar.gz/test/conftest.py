#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, inspect, pytest

# import logging
# logging.basicConfig(level = logging.DEBUG)

is_generate = False
fname = None

def localize_fname(modfname, fname):
	dname = os.path.dirname(modfname)
	fname = os.path.join(dname, fname)
	return fname

def pytest_addoption(parser):
    parser.addoption("--generate", action="store_true", help="generate output validation files")

def define_args(modfname, params, ids):
	'''Base (mutualized) factory function to define test fixture.'''
	@pytest.fixture(params = params, ids = ids)
	def args(request):
		'''List of command line arguments, used by cmdline object.'''
		global is_generate, fname

		is_generate = request.config.getoption('--generate')
		fname = os.path.splitext(os.path.basename(modfname))[0]
		fname = '%s_%s.out' % (fname, ids[request.param_index])
		fname = localize_fname(modfname, fname)
		return request.param
	return args

def define_test(entry_point):
	'''Base (mutualized) factory function to define test function.'''
	def test(capsys, args):
		# log = logging.getLogger('test_main')
		# log.debug('- entering test_main ...')
		out, err = capsys.readouterr()
		entry_point(args)
		out, err = capsys.readouterr()
		if is_generate:
			file(fname, 'wt').write(out)
		else:
			expect = file(fname, 'rt').read()
			assert out == expect
		# log.debug('- exiting test_main ...')
	return test
