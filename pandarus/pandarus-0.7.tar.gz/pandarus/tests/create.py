# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

import fiona
from fiona import crs as fiona_crs
import os


wgs84 = fiona_crs.from_string("+datum=WGS84 +ellps=WGS84 +no_defs +proj=longlat")
schema = {
    'geometry': 'Polygon',
    'properties': {
        u'name': 'str:22',
    }
}


def create_record(name, coords):
    return {
        'geometry': {'coordinates': coords, 'type': 'Polygon'},
        'properties': {'name': name}
    }


def create_test_file(filepath, records, driver='GeoJSON', crs=wgs84):
    assert not os.path.exists(filepath)
    with fiona.drivers():
        with fiona.open(filepath, 'w', driver=driver, crs=crs, schema=schema) as outfile:
            for record in records:
                outfile.write(record)


def create_box(x, y, width, height):
    return [[
        (x, y),
        (x, y + height),
        (x + width, y + height),
        (x + width, y),
        (x, y)
    ]]


def create_grid(start_x=0.0, start_y=0.0, cols=10, rows=10, width=1.0,
        height=1.0):
    data = []
    for x_increment in range(cols):
        for y_increment in range(rows):
            data.append(create_box(
                start_x + x_increment * width,
                start_y + y_increment * height,
                width,
                height,
                ))
    return data


def create_grid_file(x, y, cols, rows, filepath):
    names = ["grid-cell(%s, %s)" % (i, j)
        for i in range(cols)
        for j in range(rows)
    ]
    cells = create_grid(x, y, cols, rows)
    create_test_file(
        filepath,
        [create_record(name, coords) for name, coords in zip(names, cells)]
    )
