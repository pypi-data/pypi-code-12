#
# otopi -- plugable installer
# Copyright (C) 2012-2014 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#


"""
Module contains set of helpers used in this library.
"""


def split_valid_options(string):
    """
    This function is used to unescape and split QValidValues data.
    """
    voptions = []
    option = ""
    last_c = None
    for c in string:
        if last_c == '\\':
            if c == '\\':
                option += '\\'
                last_c = None
            elif c == '|':
                option += '|'
                last_c = c
            else:
                raise ValueError(
                    "Unescaped '\\' in the valid options: %s" % string
                )
        elif c == '\\':
            last_c = c
        elif c == '|':
            voptions.append(option)
            option = ""
            last_c = c
        else:
            option += c
            last_c = c
    if option:
        voptions.append(option)
    return voptions
