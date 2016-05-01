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

# nix-type base32

import numconv

# See `libutil/hash.cc'.
nix_base32_chars = "0123456789abcdfghijklmnpqrsvwxyz"

_nix_base32 = numconv.NumConv(32, nix_base32_chars)

def nix_base32(int):
    return _nix_base32.int2str(int)

class sha256:
    def __init__(self, chksum):
        assert type(chksum) in (str, int)
        if type(chksum) is int:
            self.chksum = chksum
        elif len(chksum) == 64:
            # assume hex encoded
            self.chksum = int(chksum, 16)
        elif len(chksum) == 52:
            # assume base32 encoded
            # use nix encoding
            self.chksum = _nix_base32.str2int(chksum)

    def __str__(self):
        return self.base32()

    def __repr__(self):
        return "sha256('%s')" % self.base32()

    def base32(self):
        return nix_base32(self.chksum)

    def base16(self):
        # hex encoded
        return '%x' % self.chksum

# small tests
if __name__ == '__main__':
    h16 = 'a5e4625aef65ef7f23f54eabc1eda0748cbfa2b472976701a7e197bbe844497a'
    b32 = '19g4c9dfyrgggwizakmbq7ns0x4cpyib8wlpcw0sgqcppgl48jbs'
    c1 = sha256(h16)
    print(c1.base32())
    print(c1.base16())
    assert c1.base32() == b32
    assert c1.base16() == h16
    c2 = sha256(b32)
    assert c2.base32() == b32
    assert c2.base16() == h16
