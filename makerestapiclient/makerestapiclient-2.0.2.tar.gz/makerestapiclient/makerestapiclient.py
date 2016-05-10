#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

import re
import sys

import chevron
import pkg_resources

_formatpattern = re.compile(r'\{([a-zA-Z]\w*)\}')

def make_rest_api_client(
    api: list,
    outfile = sys.stdout,
    classname: str = "Client",
    imports: list = None,
    defaultclass: str = None,
    withcontext: bool = False,
    prefix: str = '',
    ):
    if not imports:
        imports = []


    head_template = str(pkg_resources.resource_string('makerestapiclient', 'templates/head.mustache'), 'utf-8')
    endpoint_template = str(pkg_resources.resource_string('makerestapiclient', 'templates/endpoint.mustache'), 'utf-8')
    partials={key: str(pkg_resources.resource_string('makerestapiclient', 'templates/{partial}.mustache'.format(partial=key)), 'utf-8').strip() for key in ('dict', 'arglist')}

    outfile.write(chevron.render(
        template=head_template,
        data={'imports': imports, 'classname': classname, 'httpclass': defaultclass, 'context': withcontext},
        partials_dict=partials,
        ))

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

            args = [{'arg': 'self', 'name': 'self', 'comma': True}]

            getitems(args=urlargs, defaults=defaults, arglist=args)
            getitems(args=query_args, defaults=defaults, arglist=args)
            getitems(args=query_options, defaults=defaults, arglist=args, mandatory=False)

            if urlargs:
                params['needformat'] = True
                params['urlargs'] = {'args': [{'name': arg, 'value': 'self.urlquote({arg})'.format(arg=arg), 'comma': True} for arg in urlargs]}
                params['urlargs']['args'][-1]['comma'] = False

            if method in {'PUT', 'POST'}:
                getitems(args=data_args, defaults=defaults, arglist=args)
                getitems(args=data_options, defaults=defaults, arglist=args, mandatory=False)

                if data_args or data_options:
                    params['data'] = {'args': [{'key': repr(arg), 'value': arg.lower().replace('-', '_'), 'comma': True} for arg in (data_args + data_options)]}
                    params['data']['args'][-1]['comma'] = False

            if query_args or query_options:
                params['query'] = {'args': [{'key': repr(arg), 'value': arg.lower().replace('-', '_'), 'comma': True} for arg in (query_args + query_options)]}
                params['query']['args'][-1]['comma'] = False
                params['needformat'] = True

            args[-1]['comma'] = False
            params['args'] = args

            outfile.write(chevron.render(
                template=endpoint_template,
                data=params,
                partials_dict=partials,
                ))

def getitems(args, defaults, arglist, mandatory=True):
    for arg in args:
        if arg not in (item['arg'] for item in arglist):
            argitem = {'arg': arg, 'name': arg.lower().replace('-', '_'), 'comma': True}

            if arg in defaults:
                argitem['value'] = repr(defaults[arg])
            elif not mandatory:
                argitem['value'] = '_NO_VALUE'
            
            arglist.append(argitem)
