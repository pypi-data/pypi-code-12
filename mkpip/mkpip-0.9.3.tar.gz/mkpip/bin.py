#!/usr/bin/env python
import os
import sys
import argparse
import fnmatch
import shutil
from datetime import datetime
from .config import config_getter


__author__ = 'Johan Nestaas <johannestaas@gmail.com>'
__title__ = 'mkpip'
__version__ = '0.9.3'
__license__ = 'GPLv3+'
__copyright__ = 'Copyright 2016 Johan Nestaas'


def bumpv():
    from bumpy import main
    main()


def mkmod():
    from mkmod import main
    main()


def make_rewrite_dict(args):
    get = config_getter(config_name=args['config'], args=args)
    rewrite = args.copy()
    rewrite['underline'] = len(args['name']) * '='
    rewrite['author'] = get('author', '?')
    rewrite['email'] = get('email', '?')
    rewrite['year'] = get('year', datetime.now().strftime('%Y'))
    rewrite['copyright_holder'] = get('copyright_holder', rewrite['author'])
    rewrite['license_path'] = get('license_path')
    rewrite['license'] = get('license', 'GPLv3+')
    if get('url'):
        try:
            rewrite['url'] = get('url') % args['name']
        except TypeError:
            rewrite['url'] = get('url').format(**rewrite)
    else:
        rewrite['url'] = ''
    if rewrite['license'].lower().startswith('gpl'):
        license_long = (
            '\'License :: OSI Approved :: GNU General Public License v3 or '
            'later \'\n        \'({license})\','.format(**rewrite))
    elif rewrite['license'].lower().startswith('bsd'):
        license_long = '\'License :: OSI Approved :: BSD License\','
    else:
        license_long = ''
    rewrite['license_long'] = license_long
    return rewrite


def fix_filename(fname, rewrite):
    fname, ext = os.path.splitext(fname)
    if ext.lower() == '.pyt':
        ext = '.py'
    fname = fname + ext
    return fname.format(**rewrite)


def setup_dirs(name=None, dest=None, **kwargs):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bp_dir = os.path.join(base_dir, 'boilerplate')
    pip_dir = os.path.join(dest, name)
    bad_mkpip_dir = os.path.join(pip_dir, 'mkpip')
    if os.path.exists(pip_dir):
        sys.exit('{0} already exists.'.format(pip_dir))
    shutil.copytree(bp_dir, pip_dir)
    if os.path.isdir(bad_mkpip_dir):
        shutil.rmtree(bad_mkpip_dir)
    for root, dirnames, filenames in os.walk(pip_dir):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            os.remove(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, 'bin.*'):
            os.remove(os.path.join(root, filename))
    return pip_dir


def rewrite_files(pip_dir, rewrite):
    files = [
        '.gitignore',
        'setup.pyt',
        'README.rst',
        'MANIFEST.in',
        'LICENSE',
        '{name}/__init__.pyt',
        'tests/test_{name}.pyt',
    ]
    for name in files:
        path = os.path.join(pip_dir, name)
        with open(path) as f:
            r = f.read()
        new = r.format(**rewrite)
        with open(path, 'w') as f:
            f.write(new)
    if rewrite['license_path']:
        path = os.path.join(pip_dir, 'LICENSE')
        with open(rewrite['license_path']) as f:
            r = f.read()
        new = r.format(**rewrite)
        with open(path, 'w') as f:
            f.write(new)
    orig_dir = os.path.join(pip_dir, '{name}')
    new_dir = orig_dir.format(**rewrite)
    shutil.move(orig_dir, new_dir)
    orig_dir = os.path.join(pip_dir, 'tests', 'test_{name}.pyt')
    new_dir = orig_dir.format(**rewrite)
    shutil.move(orig_dir, new_dir)
    for name in files:
        path = os.path.join(pip_dir, name).format(**rewrite)
        rename, ext = os.path.splitext(path)
        if ext.lower() == '.pyt':
            ext = '.py'
        rename = rename + ext
        shutil.move(path, rename)


def mkpip():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='Name of project.')
    parser.add_argument('desc', help='Description of project. Will go in '
                        'README.rst, setup.py, and license')
    parser.add_argument('--keywords', '-k', default='',
                        help='keywords in setup.py')
    parser.add_argument('--dest', '-d', default=os.getcwd(),
                        help='Destination directory that contains project '
                        'folder (default ./$name)')
    parser.add_argument('--config', '-c', default='default',
                        help='Name of config block to use, default:%(default)s')
    parser.add_argument('--author', '-a', help='Author')
    parser.add_argument('--email', '-e', help='Author\'s email')
    parser.add_argument('--year', '-y', help='copyright year')
    parser.add_argument('--copyright-holder', '-C', help='copyright holder')
    parser.add_argument('--license-path', '--lp',
                        help='custom license template path')
    parser.add_argument('--license', '-l', help='license in setup.py')
    parser.add_argument('--url', '-r', help='url pattern for project\'s repo')

    args = parser.parse_args()
    rewrite = make_rewrite_dict(dict(args._get_kwargs()))
    pip_dir = setup_dirs(**rewrite)
    rewrite_files(pip_dir, rewrite)
