#!/usr/bin/env python
import os
import re
from subprocess import check_output
IMPORTS_STANDARD = [
    'import os',
    'import sys',
    'import json',
]
IMPORTS_REQUESTS = [
    'import requests',
]
IMPORTS_FLASK = [
    'from flask import Flask, request',
]
IMPORTS_SUBPROCESS = [
    'from subprocess import call, check_output, PIPE, Popen, CalledProcessError',
]
IMPORTS_COLLECTIONS = [
    'from collections import namedtuple',
    'from collections import defaultdict',
    'from collections import Counter',
]
IMPORTS_BOTO = [
    'from boto import connect_s3',
    'from boto import connect_ec2',
    'from boto import connect_sqs',
]
IMPORTS_MYSQLDB = [
    'import MySQLdb',
]
IMPORTS_PSYCOPG2 = [
    'import psycopg2',
]
IMPORTS_YAMLCFG = [
    'from yamlcfg import YamlConfig',
]
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'bin.py')

RE_IMP_KWARG = re.compile(r'imp_(\w+)')

def render(flags=None, opts=None, pos=None, **import_kwargs):
    if 'imp_standard' not in import_kwargs:
        import_kwargs['imp_standard'] = True
    imports = []
    for key, val in import_kwargs.items():
        if not val:
            continue
        match = RE_IMP_KWARG.match(key)
        if not match:
            print('No match on {}'.format(key))
            continue
        var = match.group(1)
        newkey = 'IMPORTS_{}'.format(var.upper())
        imports += globals()[newkey]
    with open(TEMPLATE_PATH) as f:
        temp = f.read()
    imports = '\n'.join(imports)
    args = []
    if flags is not None:
        for flag in flags.split(','):
            args += [
                "parser.add_argument('--{}', '-{}', action='store_true')".format(
                flag.lower(), flag[0])
            ]
    if opts is not None:
        for o in opts.split(','):
            opt, default = o.split('=')
            if default.isdigit():
                args += [
                    "parser.add_argument('--{}', '-{}', type=int, default={},".format(
                        opt.lower(), opt[0], default
                    )
                ]
                args += [
                    "                    help='default:%(default)s')"
                ]
            elif default.lower() in ('none', 'null'):
                args += [
                    "parser.add_argument('--{}', '-{}')".format(
                        opt.lower(), opt[0]
                    )
                ]
            else:
                args += [
                    "parser.add_argument('--{}', '-{}', default='{}',".format(
                        opt.lower(), opt[0], default
                    )
                ]
                args += [
                    "                    help='default:%(default)s')"
                ]
    if pos is not None:
        for p in pos.split(','):
            args += ["parser.add_argument('{}')".format(p)]
    if import_kwargs.get('imp_flask'):
        args += [
            "parser.add_argument('--port', '-p', type=int, default=8080)"
        ]
        flask_main = '    app.run(port=args.port)'
        flask_global = '''
app = Flask('api')

@app.route('/')
def index():
    return ''
'''.lstrip()
    else:
        flask_main = ''
        flask_global = ''

    if args:
        args = ['    '+arg for arg in args]
        args = '\n'.join(args)
    else:
        args = ''

    temp = temp.format(imports=imports, args=args, flask_main=flask_main,
        flask_global=flask_global)
    return temp

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--flags', '-F', help='name of flags')
    parser.add_argument('--pos', '-P', help='name of positionals')
    parser.add_argument('--opts', '-O', help='name of optionals')
    parser.add_argument('--output', '--out', '-o', default='bin.py',
        help='output script path')
    parser.add_argument('--boto', '-b', action='store_true',
        help='add boto connection import statements')
    parser.add_argument('--collections', '--coll', '-c', action='store_true',
        help='add collections, namedtuple and defaultdict')
    parser.add_argument('--flask', '--fl', '-f', action='store_true',
        help='add flask import and boilerplate')
    parser.add_argument('--mysqldb', '--mysql', '-m', action='store_true',
        help='add mysqldb import')
    parser.add_argument('--psycopg2', '--psql', '-p', action='store_true',
        help='add psycopg2 imports')
    parser.add_argument('--requests', '--req', '-r', action='store_true',
        help='add requests import statement')
    parser.add_argument('--standard', '--std', '-s', action='store_true',
        help='add os,sys imports')
    parser.add_argument('--subprocess', '--sub', '-S', action='store_true',
        help='add subprocess imports')
    parser.add_argument('--yamlcfg', '--ycfg', '-y', action='store_true',
        help='add yamlcfg imports')
    args = parser.parse_args()
    
    template = render(
        flags=args.flags,
        pos=args.pos,
        opts=args.opts,
        imp_standard=args.standard, 
        imp_subprocess=args.subprocess,
        imp_collections=args.collections,
        imp_requests=args.requests,
        imp_boto=args.boto,
        imp_flask=args.flask,
        imp_mysqldb=args.mysqldb,
        imp_psycopg2=args.psycopg2,
        imp_yamlcfg=args.yamlcfg,
    )
    with open(args.output, 'w') as f:
        f.write(template)
    print('Wrote to {}'.format(args.output))

if __name__ == '__main__':
    main()
