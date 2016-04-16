# -*- coding: utf-8 -*-
# Time-stamp: < ipythonutils.py (2016-02-14 11:11) >

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
"""Support for embedded *IPython* invocation.

This module is not imported into public *summer* namespace, so you
should import it directly::

    from summer import ipythonutils

"""
import inspect


def run_ipshell(banner: str=None, local_variables: dict=None):
    """Runs an embedded *IPython* interpretter at the place of your call.

    To invoke the interpreter at the place of your choice::

        from summer.ipythonutils import run_ipshell
        run_ipshell()

    Args:

        banner (str): banner (greeting) to be used

        local_variables (dict): dictionary of variables accessible through
                                ``l`` variable in invoked shell, defaults
                                to current ``locals()``

    """

    from IPython.terminal.embed import InteractiveShellEmbed
    banner1 = """
Entering embedded IPython interpreter.
See 'l' (dictionary) holding local variables of caller context.
Module 'pprint' is imported.
"""

    if banner:
        banner1 += "\n" + banner

    exit_msg = "Leaving embedded IPython interpreter"
    ipshell = InteractiveShellEmbed(banner1=banner1,
                                    exit_msg=exit_msg)
    previous_frame = inspect.currentframe().f_back
    try:
        # NOTE martin.slouf -- import pprint for debugging purposes
        import pprint
        # NOTE martin.slouf -- get locals
        l = previous_frame.f_locals
        if local_variables:
            l = local_variables
        ipshell()
    finally:
        # NOTE martin.slouf -- always delete frame in finally block to
        # prevent reference cycles
        del previous_frame
