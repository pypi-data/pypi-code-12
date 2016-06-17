# Copyright 2016 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.

import json
from jinja2 import Environment, PackageLoader


def make_columns(data):
    cols = list(
        dict(name="Date",
             data="date",
             orderable=True,
             searchable=True),
        dict(name="Text",
             data="text",
             orderable=True,
             searchable=True))
    for col in data.columns:
        if col.endswith("_word"):
            cols.append(dict(name=col[:-5],
                             data=col,
                             orderable=True,
                             searchable=True))
        elif col.endswith("_tag"):
            if len(set(data[col])) > 1:
                cols.append(dict(name=col[:-4] + "tag",
                                 data=col,
                                 orderable=True,
                                 searchable=True))

    cols.append(dict(name="Match",
                     data="match",
                     searchable=True))
    cols.append(dict(name="Token",
                     data="sentence",
                     searchable=True))

    return json.dumps(cols)


def serialize_data(data):
    return data.to_json()


def make_html(data):
    env = Environment(loader=PackageLoader("wng", "templates"))
    js = env.get_template("data.js").render(data=serialize_data(data),
                                            columns=make_columns(data))
    html = env.get_template("data.html").render(title="Data table",
                                                injectedJs=js)
    return html
