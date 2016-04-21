#!/usr/bin/env python
import os
import sys
import argparse
import fnmatch
import shutil
from datetime import datetime

from yamlcfg import YamlConfig


def bumpv():
    from bumpy import main
    main()


def mkmod():
    from mkmod import main
    main()


def fix_args(args, config):
    class EmptyConfig(object):
        def __getattr__(self, x):
            return None
    config2 = EmptyConfig()
    if args.config:
        if not os.path.exists(args.config):
            sys.exit('Configuration file doesn\'t exist: %s' % args.config)
        config2 = YamlConfig(path=args.config)
    args.author = args.author or config2.author or config.author or '?'
    args.email = args.email or config2.email or config.email or '?'
    args.year = (args.year or config2.year or config.year or
                 datetime.now().strftime('%Y'))
    args.copyright_holder = (args.copyright_holder or
                             config2.copyright_holder or
                             config.copyright_holder or
                             args.author)
    args.license_path = (args.license_path or config2.license_path or
                         config.license_path or None)
    args.license = args.license or config2.license or config.license or 'GPLv3+'
    args.url = args.url or ((config2.url or config.url or '') % args.name)


def mkpip():
    config = YamlConfig(name='mkpip')
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='Name of project.')
    parser.add_argument('desc', help='Description of project. Will go in '
                        'README.rst, setup.py, and license')
    parser.add_argument('--keywords', '-k', default='',
                        help='keywords in setup.py')
    parser.add_argument('--dest', '-d', default=os.getcwd(),
                        help='Destination directory that contains project '
                        'folder (default ./$name)')
    parser.add_argument('--config', '-c', help='Path to config specifying '
                        'author, email, etc.')
    parser.add_argument('--author', '-a', help='Author')
    parser.add_argument('--email', '-e', help='Author\'s email')
    parser.add_argument('--year', '-y', help='copyright year')
    parser.add_argument('--copyright-holder', '-C', help='copyright holder')
    parser.add_argument('--license-path', '--lp',
                        help='custom license template path')
    parser.add_argument('--license', '-l', help='license in setup.py')
    parser.add_argument('--url', '-r', help='url pattern for project\'s repo')
    args = parser.parse_args()
    fix_args(args, config)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bp_dir = os.path.join(base_dir, 'boilerplate')
    pip_dir = os.path.join(args.dest, args.name)
    bad_mkpip_dir = os.path.join(pip_dir, 'mkpip')
    if os.path.exists(pip_dir):
        print('%s already exists.' % pip_dir)
        sys.exit(1)
    shutil.copytree(bp_dir, pip_dir)
    if os.path.isdir(bad_mkpip_dir):
        shutil.rmtree(bad_mkpip_dir)
    for root, dirnames, filenames in os.walk(pip_dir):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            os.remove(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'bin.*'):
            os.remove(os.path.join(root, filename))
    if args.license.startswith('GPL'):
        license_long = (
            '\'License :: OSI Approved :: GNU General Public License v3 or '
            'later (%s)\',' % args.license)
    elif args.license.startswith('BSD'):
        license_long = '\'License :: OSI Approved :: BSD License\','
    else:
        license_long = ''
    rewrite = {
        'name': args.name,
        'desc': args.desc,
        'keywords': args.keywords,
        'underline': len(args.name) * '=',
        'author': args.author,
        'email': args.email,
        'url': args.url,
        'year': args.year,
        'copyright_holder': args.copyright_holder,
        'license': args.license,
        'license_long': license_long
    }
    files = [
        '.gitignore',
        'setup.pyt',
        'README.rst',
        'MANIFEST.in',
        'LICENSE',
        'name/__init__.pyt',
    ]
    for name in files:
        path = os.path.join(pip_dir, name)
        with open(path) as f:
            r = f.read()
        new = r % rewrite
        with open(path, 'w') as f:
            f.write(new)
    if args.license_path:
        path = os.path.join(pip_dir, 'LICENSE')
        with open(args.license_path) as f:
            r = f.read()
        new = r % rewrite
        with open(path, 'w') as f:
            f.write(new)
    for name in files:
        path = os.path.join(pip_dir, name)
        if path.endswith('.pyt'):
            shutil.move(path, path[:-1])
    name_dir = os.path.join(pip_dir, 'name')
    new_dir = os.path.join(pip_dir, rewrite['name'])
    os.system('mv %s %s' % (name_dir, new_dir))
