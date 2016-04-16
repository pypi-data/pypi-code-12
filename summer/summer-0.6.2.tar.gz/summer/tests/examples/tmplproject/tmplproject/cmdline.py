# -*- coding: utf-8 -*-
# Time-stamp: < cmdline.py (2016-01-24 16:47) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from optparse import OptionParser

# default values are not hardcoded here, but taken from config file

SHELL = "shell"

USAGE = """%%prog [command] [options] [args]

Commands:

%20s  run the ipython shell with classes from this project pre-imported
""" % (SHELL)


class MyOptionParser(OptionParser):

    def __init__(self, config):
        OptionParser.__init__(self, USAGE)
        self.config = config
        self.__add_my_options()

    def __add_my_options(self):
        self.add_option(
            "-s", "--string",
            action="store",
            type="string",
            dest="string",
            default="string option example",
            help="string option example [default: %default]",
            metavar="STRING"
        )

        self.add_option(
            "-v", "--verbose",
            action="store_true",
            dest="verbose",
            default=False,
            help="boolean option example [default: %default]"
        )

        choices = ("a", "b", "c")
        self.add_option(
            "-c", "--choice",
            action="store",
            type="choice",
            choices=choices,
            dest="choice",
            default=choices[0],
            help="choice option example can be either %s | %s | %s [default: %%default]" %
            choices
        )

        use_ldap = self.config.getboolean("DEFAULT", "use_ldap")
        self.add_option(
            "-l", "--use-ldap",
            action="store_true",
            dest="use_ldap",
            help="enforce use of LDAP"
        )

        self.add_option(
            "-L", "--do-not-use-ldap",
            action="store_false",
            dest="use_ldap",
            default=use_ldap,
            help="forbid the use of LDAP"
        )
