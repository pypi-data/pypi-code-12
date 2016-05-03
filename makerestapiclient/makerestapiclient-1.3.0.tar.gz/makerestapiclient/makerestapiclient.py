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
				methods = frozenset(('GET',))

		data_args = endpoint.get('data-args', [])
		data_options = endpoint.get('data-options', [])
		query_args = endpoint.get('query-args', [])
		query_options = endpoint.get('query-options', [])

		defaults = endpoint['defaults'] if 'defaults' in endpoint else dict()

		for method in methods:
			usedvars = set()

			defname = '{meth}_{name}'.format(meth=method.lower(), name=basename.lower().replace('-', '_'))
			args = ['self']

			for arg in urlargs:
				if arg not in usedvars:
					argitem = arg.lower().replace('-', '_')
					if arg in defaults:
						argitem += ' = {}'.format(repr(defaults[arg]))

					args.append(argitem)
					usedvars.add(arg)

			for arg in query_args:
				if arg not in usedvars:
					argitem = arg.lower().replace('-', '_')
					if arg in defaults:
						argitem += ' = {}'.format(repr(defaults[arg]))

					args.append(argitem)
					usedvars.add(arg)

			for option in query_options:
				if option not in usedvars:
					optitem = option.lower().replace('-', '_')
					if optitem in defaults:
						optitem += ' = {}'.format(repr(defaults[option]))
					else:
						optitem += ' = _NO_VALUE'

					args.append(optitem)
					usedvars.add(option)

			if method in {'PUT', 'POST'}:
				for arg in data_args:
					if arg not in usedvars:
						argitem = arg.lower().replace('-', '_')
						if arg in defaults:
							argitem += ' = {}'.format(repr(defaults[arg]))

						args.append(argitem)
						usedvars.add(arg)


				for option in data_options:
					if option not in usedvars:
						optitem = option.lower().replace('-', '_')
						if optitem in defaults:
							optitem += ' = {}'.format(repr(defaults[option]))
						else:
							optitem += ' = _NO_VALUE'

						args.append(optitem)
						usedvars.add(option)

			outfile.write(endpoint_template.render(
				name=defname,
				arglist=', '.join(args),
				description=endpoint.get('description'),
				all_query_args={arg: arg.lower().replace('-', '_') for arg in (query_args + query_options)},
				prefix=prefix,
				endpoint=endpoint['endpoint'],
				urlargs=', '.join('{arg}=self.urlquote({arg})'.format(arg=arg) for arg in urlargs),
				all_data_args={arg: arg.lower().replace('-', '_') for arg in (data_args + data_options)},
				method=method,
				))
