#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Import towns from OpenStreetMap data.
Take an OSM xml file for argument.

To get an OSM file (with a bounding box adapted to your needs):
curl --location --globoff "http://www.informationfreeway.org/api/0.6/node[place=village|town|city][bbox=-5.53711,41.90228,8.96484,51.50874]" -o city.osm
or from a whole xml/pbf export:
./osmosis --read-pbf ~/france-20110125.osm.pbf --node-key-value keyValueList="place.village,place.town,place.city" --write-xml city.osm
"""

import sys
sys.path.append('.')

from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
import settings

setup_environ(settings)

from optparse import OptionParser
from xml.parsers import expat

from ishtar_base import models

usage = "usage: %prog osm_file.xml"
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

try:
    assert len(args) == 1
except AssertionError:
    parser.error("You must provide one XML file")


ATTRS = [u"lat", u"lon"]

# key : (mandatory, [restraint to keys])
TAGS = {u"place":(True, [u"village", u"town", u"city"]),
        u"ref:INSEE":(True, []),
        u"population":(False, [])
        }

class TownParser:

    def __init__(self):
        self._parser = expat.ParserCreate()
        self._parser.returns_unicode = True
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.town = {}
        self.number = 0

    def feed(self, data):
        self._parser.ParseFile(data)

    def close(self):
        self._parser.Parse("", 1) # end of data
        del self._parser # get rid of circular references

    def start(self, tag, attrs):
        if tag == u"node":
            self.town = {}
            for attr in ATTRS:
                if attr in attrs:
                    self.town[attr] = attrs[attr]
        if tag == u"tag":
            if not u"k" in attrs or not u"v" in attrs:
                return
            if attrs[u"k"] in TAGS:
                limit = TAGS[attrs[u"k"]][1]
                if limit and \
                   (attrs[u"v"] not in limit or \
                   (type(limit) == unicode and limit not in attrs[u"v"])):
                    self.town["DEL"] = True
                    return
                self.town[attrs[u"k"]] = attrs[u"v"]

    def end(self, tag):
        if tag == u"node" and self.town and "DEL" not in self.town:
            for k in TAGS:
                if TAGS[k][0] and k not in self.town:
                    return
            self.number += 1
            try:
                town = models.Town.objects.get(numero_insee=self.town["ref:INSEE"])
            except ObjectDoesNotExist:
                return
            town.center = Point(float(self.town['lon']), float(self.town['lat']),
                                srid=4326)
            town.save()
            print town, "updated"

    def data(self, data):
        pass

p = TownParser()

try:
    p.feed(file(args[0]))
    print u"%d towns updated" % p.number
except (IOError, expat.ExpatError):
    parser.error("Incorrect XML file")


