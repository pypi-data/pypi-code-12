import os
from distutils.dir_util import copy_tree
import subprocess
import sys
import textwrap


def _copy_package(src, dst, package):
    parts = package.split('.')
    for i in range(1, len(parts)):
        folder = os.path.join(dst, *parts[:i])
        os.makedirs(folder)
        open(os.path.join(folder, '__init__.py'), 'w').write(textwrap.dedent('''
            # this is a namespace package
            try:
                import pkg_resources
                pkg_resources.declare_namespace(__name__)
            except ImportError:
                import pkgutil
                __path__ = pkgutil.extend_path(__path__, __name__)
        ''').strip())
    return os.path.join(*parts)


def copy(src, dst, vars):
    if os.path.isdir(src):
        os.makedirs(dst)
        for srcfile in os.listdir(src):
            if srcfile == '__PACKAGE_NAME__' and \
                    os.path.isdir(os.path.join(src, srcfile)):
                dstfile = _copy_package(src, dst, vars['__PACKAGE_NAME__'])
            else:
                dstfile = srcfile
                for k, v in vars.items():
                    dstfile = dstfile.replace(k, v)
            copy(os.path.join(src, srcfile), os.path.join(dst, dstfile), vars)
    else:
        try:
            content = open(src).read()
            for k, v in vars.items():
                content = content.replace(k, v)
            open(dst, 'w').write(content)
        except UnicodeDecodeError:
            # not a text file, just copy content
            open(dst, 'wb').write(open(src, 'rb').read())


def srcvalid(src):
    return (src.startswith('git+') or
            src.startswith('git:') or
            src.startswith('hg+') or
            os.path.isdir(src) or
            os.path.isdir(os.path.join(
                os.path.dirname(__file__), 'scaffolds', src)))


def prepare(src, dst):
    if src.startswith('git+'):
        download_git(src[4:], dst)
    elif src.startswith('git:'):
        download_git(src, dst)
    elif src.startswith('hg+'):
        download_hg(src[3:], dst)
    elif os.path.isdir(src):
        copy_tree(src, dst)
    elif os.path.isdir(os.path.join(os.path.dirname(__file__),
                                    'scaffolds', src)):
        src = os.path.join(os.path.dirname(__file__), 'scaffolds', src)
        copy_tree(src, dst)
    else:
        raise ValueError('Could not determine how to prepare from %s' % src)


def download_git(src, dst):
    subprocess.check_call(
        ['git', 'clone', src, dst],
        stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def download_hg(src, dst):
    subprocess.check_call(
        ['hg', 'clone', src, dst],
        stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
