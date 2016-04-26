# -*- coding: utf-8 -*-
'''
This module validates a polygon in Flanders.
'''

import colander
import json
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from oe_geoutils.utils import get_srid_from_geojson
import logging

log = logging.getLogger(__name__)


def geometrie_validator(node, gj, max_area):
    """
    Validate a geojson if it is a valid geometry.
    Function checks if a geojson is a valid geometry.
    Current checks are:
    *Type of geometry must be geojson
    *geometry must be valid according to OGC-specifications
    *geometry must be inside bounding box of Flanders
    *geometry must be smaller than the given max_area
    :param node: A colander SchemaNode.
    :param gj: geojson to be validated
    :raise colander.Invalid: when geojson does not satisfy the upper conditions
    """
    if gj is None or not gj:
        raise colander.Invalid(node, "geometrie is verplicht en mag niet leeg zijn")
    try:
        geom = shape(gj)
        if geom.type != "MultiPolygon":
            raise colander.Invalid(node, 'geometrie is niet van het type MultiPolygon')
        srid = get_srid_from_geojson(gj)
        if srid is None or srid != 31370:
            raise colander.Invalid(node,
                                   'Geen geldige srid gevonden. '
                                   'Enkel geometrien met srid 31370 (Lambert 72) worden ondersteund')
        if geom.is_empty or not geom.is_valid or not geom.is_simple:
            geom = unary_union(geom)
            if geom.is_empty or not geom.is_valid or not geom.is_simple:
                raise colander.Invalid(node,
                                       'Geometrie is niet geldig '
                                       '(bv: leeg, voldoet niet aan OGC, zelf-intersecterend,...)')
            gj.update(json.loads(json.dumps(mapping(geom))))
            if gj['type'] == 'Polygon':
                gj.update({'type': 'MultiPolygon', 'coordinates': [gj['coordinates']]})
        if geom.area > max_area:
            raise colander.Invalid(node, 'Geometrie is {} ha, groter dan {} ha, '
                                         'gelieve de polygoon te verkleinen.'.format(geom.area / 10000,
                                                                                     max_area / 10000))

        b = box(19680.692555495727, 146642.51885241456, 274994.53266103653,
                245606.4642544454)  # bounding box vlaanderen
        if not b.contains(geom):
            raise colander.Invalid(node, 'Geometrie ligt niet binnen de bounding box van Vlaanderen')
        return gj
    except ValueError:
        raise colander.Invalid(node, 'geometrie is geen geldig GeoJson')


class GeoJson(colander.SchemaType):
    """ GeoJson object Type """

    def serialize(self, node, appstruct):
        raise NotImplementedError()

    def deserialize(self, node, cstruct):
        if cstruct != 0 and not cstruct:
            return colander.null
        try:
            return self.build_shape(cstruct)
        except Exception:
            raise colander.Invalid(node, "Geen geldige GeoJson: %s" % cstruct)

    @staticmethod
    def build_shape(cstruct):
        """
        converts a value into GeoJson (if valid)
        raises a colander.Invalid if value cannot be transformed into GeoJson
        :param cstruct: The structure to be validated
        :return: geojson
        :raise colander.Invalid: when the value is no valid geojson
        """
        if cstruct is None or not cstruct:
            return None
        s = json.dumps(cstruct)
        g1 = json.loads(s)
        shape(g1)
        return g1


class GeometrieSchemaNode(colander.SchemaNode):
    title = 'geometrie'
    schema_type = GeoJson
    max_area = 8000

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and isinstance(args[0], int):
            self.max_area = args[0]
            args = args[1:]
        super(GeometrieSchemaNode, self).__init__(*args, **kwargs)
        try:
            self.max_area = float(self.max_area) * 10000
        except ValueError:
            log.error("oe_geoutils: invalid configuration for max area geometry: {}".format(self.max_area))
            self.max_area = 80000000

    def validator(self, node, cstruct):
        return geometrie_validator(node, cstruct, self.max_area)
