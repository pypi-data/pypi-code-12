#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

import re
import sys

import pystache
import pkg_resources

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

	head_template = pystache.parse(str(pkg_resources.resource_string('makerestapiclient', 'templates/head.mustache'), 'utf-8'))
	endpoint_template = pystache.parse(str(pkg_resources.resource_string('makerestapiclient', 'templates/endpoint.mustache'), 'utf-8'))
	stache = pystache.Renderer(escape=lambda u: u,)

	outfile.write(stache.render(head_template, {'imports': imports, 'classname': classname, 'httpclass': defaultclass, 'context': withcontext}))

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
			methods = tuple(sorted(endpoint['methods']))
		else:
			if endpoint.get('data-args') or endpoint.get('data-options'):
				methods = ('DELETE', 'GET', 'PUT')
			else:
				methods = ('GET',)

		data_args = endpoint.get('data-args', [])
		data_options = endpoint.get('data-options', [])
		query_args = endpoint.get('query-args', [])
		query_options = endpoint.get('query-options', [])

		defaults = endpoint['defaults'] if 'defaults' in endpoint else dict()

		for method in methods:
			params = {
				'smallmethod': method.lower(),
				'name': basename.lower().replace('-', '_'),
				'description': endpoint.get('description', False),
				'prefix': prefix,
				'endpoint': endpoint['endpoint'],
				'method': method,
				}

			args = [{'arg': 'self', 'name': 'self'}]

			getitems(args=urlargs, defaults=defaults, arglist=args)
			getitems(args=query_args, defaults=defaults, arglist=args)
			getitems(args=query_options, defaults=defaults, arglist=args, mandatory=False)

			if urlargs:
				params['needformat'] = True
				params['urlargs'] = ', '.join('{arg}=self.urlquote({arg})'.format(arg=arg) for arg in urlargs)

			if method in {'PUT', 'POST'}:
				getitems(args=data_args, defaults=defaults, arglist=args)
				getitems(args=data_options, defaults=defaults, arglist=args, mandatory=False)

				if data_args or data_options:
					params['data'] = {'args': [{'key': repr(arg), 'value': arg.lower().replace('-', '_')} for arg in (data_args + data_options)]}

			if query_args or query_options:
				params['query'] = {'args': [{'key': repr(arg), 'value': arg.lower().replace('-', '_')} for arg in (query_args + query_options)]}
				params['needformat'] = True

			params['args'] = args

			outfile.write(stache.render(endpoint_template, params))

def getitems(args, defaults, arglist, mandatory=True):
	for arg in args:
		if arg not in (item['arg'] for item in arglist):
			argitem = {'arg': arg, 'name': arg.lower().replace('-', '_')}

			if arg in defaults:
				argitem['value'] = repr(defaults[arg])
			elif not mandatory:
				argitem['value'] = ' = _NO_VALUE'
			
			arglist.append(argitem)
