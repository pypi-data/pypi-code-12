#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

import re
import sys

from jinja2 import Environment, PackageLoader

_formatpattern = re.compile(r'\{([a-zA-Z]\w*)\}')

def make_rest_api_client(
	api: list,
	outfile = sys.stdout,
	classname: str = "Client",
	imports: list = None,
	defaultclass: str = None,
	indent: str = '    ',
	withcontext: bool = False,
	prefix: str = '',
	):
	if not imports:
		imports = []

	env = Environment(loader=PackageLoader('makerestapiclient', 'templates'))
	head = env.get_template('head.py')
	endpoint_template = env.get_template('endpoint.py')
	outfile.write(head.render(imports=imports, classname=classname, httpclass=defaultclass, withcontext=withcontext))

	# Build the API endpoint
	for endpoint in api:
		# Get basename of method
		if endpoint.get('name'):
			basename = endpoint['name']
		else:
			basename = endpoint['endpoint']

		urlargs = _formatpattern.findall(endpoint['endpoint'])

		# Get or infer methods
		if endpoint.get('methods'):
			methods = frozenset(endpoint['methods'])
		else:
			if endpoint.get('data-args') or endpoint.get('data-options'):
				methods = frozenset({'GET', 'PUT', 'DELETE'})
			else:
				methods = frozenset({'GET',})

		data_args = endpoint.get('data-args', [])
		data_options = endpoint.get('data-options', [])
		query_args = endpoint.get('query-args', [])
		query_options = endpoint.get('query-options', [])

		defaults = endpoint['defaults'] if 'defaults' in endpoint else dict()

		for method in methods:
			usedvars = set()

			args = ['self']

			getitems(args=urlargs, usedvars=usedvars, defaults=defaults, arglist=args)
			getitems(args=query_args, usedvars=usedvars, defaults=defaults, arglist=args)
			getitems(args=query_options, usedvars=usedvars, defaults=defaults, arglist=args, mandatory=False)

			if method in {'PUT', 'POST'}:
				getitems(args=data_args, usedvars=usedvars, defaults=defaults, arglist=args)
				getitems(args=data_args, usedvars=usedvars, defaults=defaults, arglist=args, mandatory=False)

			outfile.write(endpoint_template.render(
				name=basename.lower().replace('-', '_'),
				arglist=args,
				description=endpoint.get('description'),
				all_query_args=(query_args + query_options),
				prefix=prefix,
				endpoint=endpoint['endpoint'],
				urlargs=', '.join('{arg}=self.urlquote({arg})'.format(arg=arg) for arg in urlargs),
				all_data_args=(data_args + data_options),
				method=method,
				))

def getitems(args, usedvars, defaults, arglist, mandatory=True):
	for arg in args:
		if arg not in usedvars:
			argitem = arg.lower().replace('-', '_')

			if arg in defaults:
				argitem += ' = {}'.format(repr(defaults[arg]))
			elif not mandatory:
				argitem += ' = _NO_VALUE'
			
			arglist.append(argitem)
			usedvars.add(arg)
