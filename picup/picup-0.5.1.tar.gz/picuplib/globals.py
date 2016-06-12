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
Module for some "global" constants
"""

from .misc import gen_user_agent

__version__ = '0.5.2'

API_URL = 'https://www.picflash.org/tool.php'

ALLOWED_RESIZE = ('80x80', '100x75', '100x100', '150x112', '468x60', '400x400',
                  '320x240', '640x480', '800x600', '1024x768', '1280x1024',
                  '1600x1200', 'og')

ALLOWED_ROTATION = ('00', '90', '180', '270')

USER_AGENT = gen_user_agent(__version__)
