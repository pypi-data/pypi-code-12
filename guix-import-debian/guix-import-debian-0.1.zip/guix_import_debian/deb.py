# -*- coding: utf-8 -*-
# Guix Import Debian --- Import helper for GNU Guix
# Copyright © 2016 Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import pprint
import tarfile
import shutil
import textwrap
import re

import warnings
warnings.filterwarnings('ignore', 'cannot parse package relationship .*, returning it raw')

from debian import deb822

from . import query
from .base32 import sha256

try:
    # "backport" xztar (was implemented in 3.5 only)
    import lzma
    del lzma
    shutil.register_unpack_format('xztar',['.tar.xz', '.txz'], 
                                  shutil._unpack_tarfile)
except ImportError:
    pass


def get_dependencies(ctlpkg, pkginfo):
    for dep in ('depends', 'build-depends', 'build-depends-indep'):
        if dep in ctlpkg:
            pkginfo[dep] = deb822.PkgRelation.parse_relations(ctlpkg[dep])
        else:
            pkginfo[dep] = []

def dsc2pkginfo(dsc):
    pkginfo = {
        'name': dsc['source'],
        'binaries': [b.strip() for b in dsc['binary'].split(',')],
        'version': dsc['version'],
        'homepage': dsc['homepage'],
    }
    files = [(f['name'], sha256(f['sha256']))
             for f in dsc['checksums-sha256']]
    pkginfo['patches'] = dict((n, c) for (n,c) in files if '.patch' in n)
    pkginfo['debianarch'] = dict((n, c) for (n,c) in files 
                                 if dsc['version'] + '.debian.tar' in n)
    pkginfo['sources'] = dict((n, c) for (n,c) in files 
                              if (n not in pkginfo['patches'] and 
                                  n not in pkginfo['debianarch']))
    assert len(pkginfo['debianarch']) == 1
    assert len(pkginfo['patches']) + len(pkginfo['debianarch']) + len(pkginfo['sources']) == len(files)

    get_dependencies(dsc, pkginfo)

    return pkginfo

def unpack_archive(archivefile, destdir):
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    shutil.unpack_archive(archivefile, destdir)

WATCH_URL = re.compile(r'((http|https|ftp)://\S+)')

def get_watch_url(archive_dir, pkginfo):
    # collect relevant information from debian/watch file

    def get_watch(archive_dir):
        # :todo: adopt this to handle watchfile specification
        with open(os.path.join(archive_dir, 'debian', 'watch')) as fh:
            text = fh.readlines()
        # Parse accoding to `man uscan`
        last = None
        for l in text:
            l = l.lstrip() # Leading spaces and tabs are dropped
            if not l or l.startswith('#'):
                # Empty lines are dropped.
                # A line started by # (hash) is a comment line and dropped.
                continue
            if last is not None:
                l = last + l
                last = None
            if l.endswith('\\'):
                last = l
                continue
            m = WATCH_URL.search(l)
            if m:
                return m.group(0)

    url = get_watch(archive_dir)
    url = url.replace('\\.', '.')
    p = url.split('(.*)')
    pkginfo['uri'] = '"%s"' % '" version "'.join(p)


def get_packages(archive_dir, pkginfo):
    # collect relevant information from debian/control file
    with open(os.path.join(archive_dir, 'debian', 'control')) as fh:
        text = fh.readlines()
    pkginfo['package'] = pkgs = []
    for ctlpkg in deb822.Packages.iter_paragraphs(text):
        if 'source' in ctlpkg:
            continue
        pkg = {
            'name': ctlpkg['package'],
            'depends': ctlpkg['depends'],
            }
        pkgs.append(pkg)
        pkg['synopsis'], description = ctlpkg['description'].split('\n', 1)
        description = textwrap.dedent(description).strip()
        description = description.replace('\n.\n', '\n\n')
        pkg['description'] = description
        get_dependencies(ctlpkg, pkg)
    
def get_license(archive_dir, pkginfo):
    pkginfo['license'] = 'unknown'
    with open(os.path.join(archive_dir, 'debian', 'copyright')) as fh:
        text = fh.readlines()
    for l in text:
        if l.startswith('License: '):
            pkginfo['license'] = l.split(None, 1)[1].strip()

def collect_info(packagename, cachedir):
    vers = query.get_pkg_versions(packagename)
    vers.sort(reverse=True) # :todo: sort semantically
    ver, area = vers[0]
    dsc = query.get_pkg_dsc(packagename, ver, area)
    dsc = deb822.Dsc(dsc)

    pkginfo = dsc2pkginfo(dsc)

    # download and unpack the .debian archive
    filename = list(pkginfo['debianarch'].keys())[0]
    archivefile = os.path.join(cachedir, filename)
    query.store_pkg_debian_arch(filename, packagename, area, archivefile)
    archive_dir = os.path.join(cachedir, '{name}-{version}'.format(**pkginfo))
    unpack_archive(archivefile, archive_dir)

    get_watch_url(archive_dir, pkginfo)
    get_packages(archive_dir, pkginfo)
    get_license(archive_dir, pkginfo)

    return pkginfo, archive_dir

if __name__ == '__main__':
    packagename = 'commons-io'
    cachedir = '/tmp'
    pkginfo, outfilename = collect_info(packagename, cachedir)

    pprint.pprint(pkginfo)
    print(outfilename)
