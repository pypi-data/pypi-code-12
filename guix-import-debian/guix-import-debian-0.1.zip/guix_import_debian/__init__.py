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

__version__ = '0.1'

from . import deb
from .mappings import DEBIAN_LICENSE_MAP

import pprint

template = """
(define-public {name}-{version}
  (package
    (name "{name}")
    (version "{version}")
    (source (origin
      (method url-fetch)
      (uri (string-append
            {uri}))
      (sha256 (base32 "{sha256}"))))
    (build-system {build_system})
    (inputs
     `({inputs}))
    (native-inputs
     `({native_inputs}))
    (homepage "{homepage}")
    (synopsis "{synopsis}")
    (description "{description}")
    (license {license})
))
"""

class Input:
    def __init__(self, name, version=None, comment=None, **kw):
        self.name = name
        self.version = ' '.join(version or ())
        self.comment = comment

    def __eq__(self, other):
        return self.name.__eq__(other)

    def __str__(self):
        s = '("{0.name}" ,{0.name})'.format(self)
        if self.version and self.comment:
            s = s + ' ; {0.version} - {0.comment}'.format(self)
        elif self.version:
            s = s + ' ; {0.version}'.format(self)
        elif self.comment:
            s = s + ' ; {0.comment}'.format(self)
        return s

    def __repr__(self):
        if self.version:
            return 'Input(name={0.name!r}, version={0.version!r})'.format(self)
        else:
            return 'Input(name={0.name!r})'.format(self)

DEPENDS_TO_IGNORE = ['${misc:Depends}']

class Inputs(list):
    def __init__(self, pkginfo, *kind):

        def collect_inputs(pkg):
            for k in kind:
                for i in pkg[k]:
                    comment = None
                    if i[0]['name'] in names:
                        continue
                    names.add(i[0]['name'])
                    if len(i) > 1:
                        comment = ' | '. join(str(j for j in i))
                    inputs.append(Input(comment=comment, **i[0]))

        inputs = []
        names = set(DEPENDS_TO_IGNORE)

        collect_inputs(pkginfo)
        for pkg in pkginfo['package']:
            collect_inputs(pkg)

        super().__init__(inputs)

    def remove(self, input):
        '''Remove element if it exists.'''
        if isinstance(input, Input):
            input = input.name
        for i, ip in enumerate(self):
            if ip == input:
                del self[i]        

    def __str__(self):
        if self:
            return '\n\t'.join(str(i) for i in self) + '\n\t'
        else:
            return ''

LANGUAGES_TO_STRIP_FROM_NAME = ('python', 'java', 'ruby')

def guess_language(pkginfo):
    name = pkginfo['name']
    for lang in LANGUAGES_TO_STRIP_FROM_NAME:
        if name.startswith(lang + '-') or name == lang:
            # already in required format
            return None
        elif lang in name:
            return lang
    # use the first package's name to check if this is a library
    if not pkginfo['package'][0]['name'].startswith('lib'):
        return None
    if 'ant' in pkginfo['native_inputs']:
        return 'java'
    # did not find a language
    return None

def change_name_for_language(pkginfo):
    lang = guess_language(pkginfo)
    if lang:
        if lang in LANGUAGES_TO_STRIP_FROM_NAME:
            pkginfo['name'] = lang + '-' + pkginfo['name'].replace(lang, '')
        else:
            pkginfo['name'] = lang + '-' + pkginfo['name']

def guess_build_system(pkginfo):
    build_system = 'trivial-build-system'
    to_remove = []
    if 'ant' in pkginfo['native_inputs']:
        build_system = 'ant-build-system'
        to_remove= ['ant', 'default-jdk']
    elif pkginfo['name'].startswith('python-'):
        build_system = 'python-build-system'
        to_remove= ['python']
    elif pkginfo['name'].startswith('perl-'): # :fixme:
        build_system = 'perl-build-system'
        to_remove= ['perl']
    pkginfo['build_system'] = build_system
    for i in to_remove:
        pkginfo['native_inputs'].remove(i)


def pkginfo2package(packagename, cachedir):
    pkginfo, outfilename = deb.collect_info(packagename, cachedir)
    # assume the first source in the list is the "main" source
    pkginfo['sha256'] = pkginfo['sources'][list(pkginfo['sources'].keys())[0]]
    # use the first package's synsopsis and description
    pkginfo['synopsis'] = pkginfo['package'][0]['synopsis']
    pkginfo['description'] = pkginfo['package'][0]['description']
    pkginfo['version'], pkginfo['revision'] = pkginfo['version'].split('-',1)

    pkginfo['inputs'] = Inputs(pkginfo, 'depends')
    pkginfo['native_inputs'] = Inputs(pkginfo, 'build-depends', 'build-depends-indep')
    for i in pkginfo['inputs']:
        pkginfo['native_inputs'].remove(i)

    if pkginfo['license'] in DEBIAN_LICENSE_MAP:
        pkginfo['license'] = DEBIAN_LICENSE_MAP.get(pkginfo['license'])

    change_name_for_language(pkginfo)
    guess_build_system(pkginfo)

    print(template.format(**pkginfo))
