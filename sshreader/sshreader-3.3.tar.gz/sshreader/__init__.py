# coding=utf-8
"""A Python Package for parallelizing ssh connections via multi-threading and multi-processing.
"""
# Copyright (C) 2015 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function, absolute_import
from pkg_resources import get_distribution, DistributionNotFound

# For backwards compatibility
from sshreader.ssh import SSH, shell_command, do_shell_script, envvars
from sshreader.sshreader import ServerJob, Hook, sshread, print_results, echo, cpusoftlimit, cpuhardlimit

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'
try:
    __version__ = get_distribution('sshreader').version
except DistributionNotFound:
    __version__ = 'UNKNOWN'
__all__ = ['sshreader', 'ssh']
