#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

import re
import sys

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

	if imports:
		outfile.writelines('{}\n'.format(imp.strip()) for imp in imports)

	outfile.write('\n')
	outfile.write('''
class {name}(object):
{i}_NO_VALUE = object()
{i}
{i}def __init__(self, scheme, host, port, username, password, httpclass{defaultclass}):
{i}{i}self.connection = httpclass(
{i}{i}{i}scheme=scheme,
{i}{i}{i}host=host,
{i}{i}{i}port=port,
{i}{i}{i}username=username,
{i}{i}{i}password=password,
{i}{i}{i})
{i}{i}self.urlquote = httpclass.urlquote
{i}{i}self.queryencode = httpclass.queryencode
'''.format(
			name=classname,
			defaultclass=(' = {}'.format(defaultclass) if defaultclass else ''),
			i=indent,
			)
		)

	if withcontext:
		outfile.write('''
{i}def __enter__(self):
{i}{i}self._old_connection = self.connection
{i}{i}self.connection = self.connection.__enter__()
{i}{i}return self

{i}def __exit__(self, type, value, traceback):
{i}{i}self._old_connection.__exit__(type, value, traceback)
{i}{i}self.connection = self._old_connection
{i}{i}del self._old_connection
'''.format(
			name=classname,
			defaultclass=(' = {}'.format(defaultclass) if defaultclass else ''),
			i=indent,
			)
		)

	outfile.write('\n')

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
			datamethod = method in {'PUT', 'POST'}
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

			if datamethod:
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

			outfile.write('\n{i}def {name}({args}):\n'.format(i=indent, name=defname, args=', '.join(args)))
			if 'description' in endpoint:
				outfile.write("{i}{i}'''{description}'''\n\n".format(i=indent, description=endpoint['description']))

			if query_args or query_options:
				outfile.write('{i}{i}_all_query_args = {{{args}}}\n'.format(
					i=indent,
					args=', '.join("'{arg}': {var}".format(arg=arg, var=arg.lower().replace('-', '_')) for arg in (query_args + query_options))))
				outfile.write('{i}{i}_query_args = {{k: v for k, v in _all_query_args.items() if v != self._NO_VALUE}}\n'.format(i=indent))
				outfile.write('{i}{i}if _query_args:\n'.format(i=indent))
				outfile.write('{i}{i}{i}_query_string = "?" + self.queryencode(_query_args)\n'.format(i=indent))
				outfile.write('{i}{i}else:\n'.format(i=indent))
				outfile.write('{i}{i}{i}_query_string = ""\n'.format(i=indent))
			else:
				outfile.write('{i}{i}_query_string = ""\n'.format(i=indent))


			outfile.write('{i}{i}_api_endpoint = "{prefix}{endpoint}{{querystring}}".format(querystring=_query_string, {urlargs})\n'.format(
				i=indent,
				prefix=prefix,
				endpoint=endpoint['endpoint'],
				urlargs=', '.join('{arg}=self.urlquote({arg})'.format(arg=arg) for arg in urlargs)))

			if datamethod:
				outfile.write('{i}{i}_all_data_args = {{{args}}}\n'.format(
					i=indent,
					args=', '.join("'{arg}': {var}".format(arg=arg, var=arg.lower().replace('-', '_')) for arg in (data_args + data_options))))
				outfile.write('{i}{i}_data_args = {{k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}}\n'.format(i=indent))
				outfile.write("{i}{i}return self.connection.{method}(endpoint=_api_endpoint, data=_data_args)\n".format(i=indent, method=method))
			else:
				outfile.write("{i}{i}return self.connection.{method}(endpoint=_api_endpoint)\n".format(i=indent, method=method))
