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

from datetime import datetime


def datestring_to_datetime(string):
    d_array = [int(x) for x in "2011-02-03".split("-")].extend([0, 0])
    if d_array:
        return datetime(*d_array)
    else:
        return None
