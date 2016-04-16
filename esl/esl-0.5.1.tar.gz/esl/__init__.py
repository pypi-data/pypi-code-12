# @Author: BingWu Yang <detailyang>
# @Date:   2016-03-30T20:49:47+08:00
# @Email:  detailyang@gmail.com
# @Last modified by:   detailyang
# @Last modified time: 2016-04-16T15:23:53+08:00
# @License: The MIT License (MIT)


import requests
from requests.status_codes import _codes
import sys

from eslyacc import parse
from eslast import *
from eslgenerator import ESLGenerator
from eslyacc import parse
from eslast import QueryStringNode, HeaderNode, BodyNode, ValueNode, ShellNode
from formatter import ColorFormatter

__version__ = '0.5.1'


def esl():
    _map = {
        'GET': requests.get,
        'POST': requests.post,
        'DELETE': requests.delete,
        'PUT': requests.put
    }
    ast = parse(' '.join(sys.argv[1:]))
    if ast is not None:
        url = ast.left.url
        method = ast.method.name
        params = {}
        headers = {}
        body = {}
        for option in ast.right.options if ast.right else []:
            if isinstance(option.key, QueryStringNode):
                if isinstance(option.value, ValueNode):
                    params[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    params[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, HeaderNode):
                headers[option.key.key] = option.value.value
            elif isinstance(option.key, BodyNode):
                body[option.key.key] = option.value.value
        try:
            r = _map[method](url, data=body, params=params, headers=headers)
            cf = ColorFormatter()
            print('%d %s' % (r.status_code, _codes[r.status_code][0]))
            for k, v in r.headers.iteritems():
                print(cf.format_headers('%s: %s' % (k, v)))
            print(cf.format_body(r.text, r.headers.get('Content-Type', 'text/html')))
        except (requests.exceptions.InvalidURL, requests.exceptions.MissingSchema):
            print('InvalidURL')

def eslgo():
    ast = parse(' '.join(sys.argv[1:]))
    if ast is not None:
        generator = ESLGenerator(ast)
        print(generator.to_go())

def eslpython():
    ast = parse(' '.join(sys.argv[1:]))
    if ast is not None:
        generator = ESLGenerator(ast)
        print(generator.to_python())

def eslcurl():
    ast = parse(' '.join(sys.argv[1:]))
    if ast is not None:
        generator = ESLGenerator(ast)
        print(generator.to_curl())
