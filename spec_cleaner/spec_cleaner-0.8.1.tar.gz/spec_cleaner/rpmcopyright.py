# vim: set ts=4 sw=4 et: coding=UTF-8

import os
import datetime

from .rpmsection import Section


class RpmCopyright(Section):

    """
    Class that always creates default SUSE copyright.
    Keeps around Copyrights of other uses and some of the build defines
    that are still relevant. Everything else is ignored.
    """

    def __init__(self, specfile, minimal):
        Section.__init__(self, specfile, minimal)
        self.copyrights = []
        self.buildrules = []
        self.my_copyright = ''
        self.vimmodeline = ''

    def _add_pkg_header(self):
        specname = os.path.splitext(os.path.basename(self.spec))[0]
        self.lines.append('''#
# spec file for package {0}
#'''.format(specname))

    def _create_default_copyright(self):
        year = datetime.datetime.now().year
        self.my_copyright = '# Copyright (c) {0} SUSE LINUX GmbH, Nuernberg, Germany.'.format(year)

    def _add_copyright(self):
        self._create_default_copyright()
        self.lines.append(self.my_copyright)

        for i in self.copyrights:
            self.lines.append(i)

    def _add_default_license(self):
        self.lines.append('''#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#''')

    def _add_buildrules(self):
        for i in sorted(self.buildrules):
            self.lines.append(i)

    def _add_modelines(self):
        # add vim modeline if found
        if self.vimmodeline:
            self.lines.append(self.vimmodeline)

    def add(self, line):
        if not self.lines and not line:
            return
        if self.reg.re_copyright.match(line) and not self.reg.re_suse_copyright.search(line):
            match = self.reg.re_copyright.match(line)
            # always replace whitespace garbage on copyright line
            line = '# Copyright (c) {0}'.format(match.group(1))
            self.copyrights.append(line)
        elif self.reg.re_rootforbuild.match(line):
            self.buildrules.append('# needsrootforbuild')
        elif self.reg.re_binariesforbuld.match(line):
            self.buildrules.append('# needsbinariesforbuild')
        elif self.reg.re_nodebuginfo.match(line):
            self.buildrules.append('# nodebuginfo')
        elif self.reg.re_icecream.match(line):
            self.buildrules.append('# icecream')
        elif self.reg.re_vimmodeline.match(line):
            self.vimmodeline = line
        else:
            # anything not in our rules gets tossed out
            return

    def output(self, fout, newline=True, new_class=None):
        self._add_modelines()
        self._add_pkg_header()
        self._add_copyright()
        self._add_default_license()
        self._add_buildrules()
        # trailing enters # prep_spec does two so do the same
        self.lines.append('')
        self.lines.append('')
        Section.output(self, fout, newline, new_class)
