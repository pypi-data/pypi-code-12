# This file is part of govtrack2csv.
#
# govtrack2csv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with govtrack2csv.  If not, see <http://www.gnu.org/licenses/>

"""
Objects we will be working with.
"""


__author__ = 'vance@hackthefed.org'


class Congress(object):
    """
    Congress is currently used only to pass data around may add it's own
    statistics to it later.

    This class has most of it's attributes assigned monkey patch style. As
    much as I hate that it's a fair bit of work to define each, so I'm
    adding them as the parsers are completed.
    """
    name = None
    legislation = None

    def __init__(self, congress):
        self.name = congress['congress']
