# -*- coding:utf8 -*-
# ####################### BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ######################## END LICENSE BLOCK #########################
"""
miscellaneous functions
"""

import requests_toolbelt

import platform


def gen_user_agent(version):
    """
    generating the user agent witch will be used for most requests

    monkey patching system and release functions from platform module
    to prevent disclosure of the OS and it's version
    """
    def monkey_patch():
        """
        small monkey patch
        """
        raise IOError

    # saving original functions
    orig_system = platform.system
    orig_release = platform.release

    # applying patch
    platform.system = monkey_patch
    platform.release = monkey_patch

    user_agent = requests_toolbelt.user_agent('picuplib', version)

    # reverting patch
    platform.system = orig_system
    platform.system = orig_release

    return user_agent
