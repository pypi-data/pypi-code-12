# ZCons
#
# Zimmermann's SCons wrapper
#
# Copyright (C) 2016 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# ZCons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZCons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ZCons. If not, see <http://www.gnu.org/licenses/>.

"""zcons.script

The zcons command line script.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
import sys

import zcons


def run():
    """Entry point for ``zcons`` command line script.

    - Calls :func:`zcons.scons` with ``sys.argv[1:]`` as arguments.
    """
    zcons.scons(*sys.argv[1:])


if __name__ == '__main__':
    run()
