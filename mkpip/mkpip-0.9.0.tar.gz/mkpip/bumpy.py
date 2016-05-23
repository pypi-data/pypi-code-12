#!/usr/bin/env python
import sys
import os
import re
from collections import namedtuple

RE_VERSION = re.compile(
    r'\s*(?:__)?version(?:__)?\s*=\s*["\']([^"\']+)["\'],?\s*')
RE_GROUPS = re.compile(r'(?P<major>\w+)\.(?P<minor>\w+)\.(?P<patch>\w+)')


class Discovery(namedtuple('Discovery', 'line_no version major minor patch')):
    pass


def line_version(path):
    with open(path) as f:
        for i, line in enumerate(f):
            match = RE_VERSION.match(line)
            if match:
                version = match.group(1)
                break
        else:
            raise ValueError('No version at {}'.format(path))
    gmatch = RE_GROUPS.match(version)
    major, minor, patch = (gmatch.group('major'), gmatch.group('minor'),
                           gmatch.group('patch'))
    return Discovery(i, version, int(major), int(minor), int(patch))


def check(path):
    line_no, version, major, minor, patch = line_version(path)
    return version


def bump_patch(path):
    d = line_version(path)
    return '{}.{}.{}'.format(d.major, d.minor, d.patch+1)


def bump_minor(path):
    d = line_version(path)
    return '{}.{}.{}'.format(d.major, d.minor+1, 0)


def bump_major(path):
    d = line_version(path)
    return '{}.{}.{}'.format(d.major+1, 0, 0)


def bump_set(path, new_version, verbose=True, dry=False):
    d = line_version(path)
    with open(path) as f:
        setup_lines = f.readlines()
    setup_lines[d.line_no] = setup_lines[d.line_no].replace(d.version,
                                                            new_version)
    if verbose:
        print('{path}: Changing {d.version} to {version}'.format(
            path=path, d=d, version=new_version))
    new_text = ''.join(setup_lines)
    if not dry:
        with open(path, 'w') as f:
            f.write(new_text)


def pushout(dirname, new_version):
    os.chdir(dirname)
    os.system('git add -u')
    os.system('git commit -am "{}"'.format(new_version))
    os.system('git tag {}'.format(new_version))
    os.system('git push --all -u')
    os.system('git push --tags')


def find_version_files(rootdir='.'):
    python_files = []
    results = []
    for root, dirnames, filenames in os.walk(rootdir):
        if '/dist/' in root or '/build/' in root:
            continue
        for fname in filenames:
            base, ext = os.path.splitext(fname)
            if ext.lower() != '.py':
                continue
            python_files += [os.path.join(root, fname)]
    for pf in python_files:
        try:
            line, version, major, minor, micro = line_version(pf)
        except ValueError:
            continue
        else:
            results += [pf]
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', '-c', action='store_true',
                        help='print current version')
    parser.add_argument('--major', '-M', action='store_true', help='bump major')
    parser.add_argument('--minor', '-m', action='store_true', help='bump minor')
    parser.add_argument('--patch', '-p', action='store_true',
                        help='bump patch level')
    parser.add_argument('--set', '-s', help='set version number')
    parser.add_argument('--root-dir', '-r', default='.',
                        help='path to root directory with files with versions')
    parser.add_argument('--push', '-P', action='store_true',
                        help='tag and push using git')
    parser.add_argument('--quiet', '-q', action='store_true')
    parser.add_argument('--dry', '-d', action='store_true')
    args = parser.parse_args()
    if args.check:
        for pf in find_version_files(args.root_dir):
            print('{path}: {version}'.format(path=pf, version=check(pf)))
        sys.exit()
    versions = set()
    changes = {}
    for pf in find_version_files(args.root_dir):
        if args.set:
            version = args.set
        elif args.minor:
            version = bump_minor(pf)
        elif args.patch:
            version = bump_patch(pf)
        elif args.major:
            version = bump_major(pf)
        else:
            version = check(pf)
        versions.add(version)
        changes[pf] = version
    if len(versions) > 1:
        sys.stderr.write('Found different versions in different files!\n')
        for path, version in sorted(changes.items()):
            sys.stderr.write('{path}: {version}\n'.format(path=path,
                                                          version=version))
        sys.exit('found various versions in files: {files}'.format(
            files=', '.join(changes.keys())))
    for pf, version in changes.items():
        bump_set(pf, version, verbose=not args.quiet, dry=args.dry)
    if args.push and not args.dry:
        pushout(args.root_dir, list(versions)[0])
