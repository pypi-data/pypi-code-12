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

import json
import requests

suite = "jessie" # current debian release

DOWNLOAD_URL_BASE = 'http://ftp.uni-erlangen.de/debian/'

class NotFoundError(Exception): pass

def get_all_packages(suite=suite):
    "Returns a list of all package-names for this suite"
    raise NotImplementedError
    #'http://sources.debian.net/api/list/?suite=%s' % suite

def search_packages(query, suite=suite):
    "Return a list of package-names matching query"
    raise NotImplementedError
    # 'http://sources.debian.net/api/search/%s' % query


def get_pkg_versions(pkgname, suite=suite):
    """
    Return a list of (version, area) tuples.

    'Area' is e.g. 'main', 'non-free'
    """
    """
{u'package': u'ocaml',
 u'path': u'ocaml',
 u'pathl': [[u'ocaml', u'/src/ocaml/']],
 u'suite': u'jessie',
 u'type': u'package',
 u'versions': [{u'area': u'main',
                u'suites': [u'jessie'],
                u'version': u'4.01.0-5'}]}
"""
    r = requests.get("http://sources.debian.net/api/src/%s/?suite=%s" % 
                     (pkgname, suite))
    data = r.json()
    if 'error' in data:
        raise NotFoundError(data['error'])
    return [(v['version'], v['area']) for v in data['versions']]


def get_pkg_dsc(pkgname, version, area):
    #http://ftp.….de/debian/pool/non-free/a/arb/arb_6.0.3-1.dsc
    url = "{base}/pool/{area}/{name[0]}/{name}/{name}_{version}.dsc".format(
        base=DOWNLOAD_URL_BASE, name=pkgname, version=version, area=area)
    print(url)
    r = requests.get(url)
    return r.text


def store_pkg_debian_arch(filename, pkgname, area, outfilename):
    #http://ftp…de/debian/pool/non-free/a/arb/arb_6.0.2-1+deb8u1.debian.tar.xz
    url = "{base}/pool/{area}/{name[0]}/{name}/{filename}".format(
        base=DOWNLOAD_URL_BASE, name=pkgname, filename=filename, area=area)
    print(url)
    r = requests.get(url)
    if r.status_code == 200:
        with open(outfilename, 'wb') as f:
            for chunk in r.iter_content(10240):
                f.write(chunk)


if __name__ == '__main__':
    try:
        print(get_pkg_versions('commonsXX-io'))
    except Exception as e:
        print(repr(e))

    name = 'commons-io'
    v1 = get_pkg_versions(name)
    print(v1)
    dsc = get_pkg_dsc(name, *v1[0])
    print(dsc)
    filename = 'commons-io_2.4-2.debian.tar.gz'
    outfilename = os.path.join('/tmp', filename)
    store_pkg_debian_arch(filename, name, v1[0][1], outfilename)
