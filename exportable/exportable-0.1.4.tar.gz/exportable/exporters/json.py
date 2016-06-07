###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import json

from exportable.exporters import Exporter


def to_row(serializers, row):
    for serializer, value in zip(serializers, row):
        if value is None:
            yield None
        elif serializer is not None:
            yield serializer(value)
        else:
            yield value


def get_serializer(column):
    if column.type in (int, float, str):
        # Internal JSON types
        return None
    return column.to_str


class JSONExporter(Exporter):
    extension = "json"
    content_type = "application/json"

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        # Order data in a json.dump friendly way
        labels = [c.label for c in table.columns]
        serializers = list(map(get_serializer, table.columns))
        row_dicts = (dict(zip(labels, to_row(serializers, row))) for row in table.rows)

        # This strange construction exists to now write a trailing comma at the end of
        # the JSON lists, without explicitly checking for last/first rows every time.
        fo.write("[".encode(encoding_hint))
        try:
            row_dict = next(row_dicts)
        except StopIteration:
            pass
        else:
            fo.write(json.dumps(row_dict, check_circular=False).encode(encoding_hint))
            for row_dict in row_dicts:
                fo.write(",".encode(encoding_hint))
                fo.write(json.dumps(row_dict, check_circular=False).encode(encoding_hint))
        finally:
            # Always write trailing parentheses
            fo.write("]".encode(encoding_hint))

