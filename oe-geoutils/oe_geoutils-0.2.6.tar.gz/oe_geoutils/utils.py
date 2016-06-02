# -*- coding: utf8 -*-
from geoalchemy2 import WKTElement, shape
import json
import geojson
import re
from shapely import geometry
import requests
import os
from operator import attrgetter


def convert_wktelement_to_geojson(wktelement):
    """
    This function converts a wktelement (from GeoAlchemy) to a geojson
    :param wktelement: WKTElement
    :return: geojson
    """
    if wktelement is None:
        return None
    try:
        geom = shape.to_shape(wktelement)
        srid = wktelement.srid
        json_element = json.dumps(geometry.mapping(geom))
        geojson_element = geojson.loads(json_element)
        geojson_element['crs'] = {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::{0}".format(srid)
            }
        }

        return geojson_element

    except AssertionError:
        raise AssertionError("WKTelement is niet geldig: %s" % wktelement)


def convert_geojson_to_wktelement(value):
    """
    This function converts a geojson to a wktelement that can be used by GeoAlchemy.
    :param value: geojson
    :return: WKTElement
    """
    if value is None or not value:
        return None
    try:
        s = json.dumps(value)
        g1 = geojson.loads(s)
        g2 = geometry.shape(g1)
        srid = get_srid_from_geojson(g1)

        return WKTElement(data=g2.wkt, srid=srid)

    except ValueError:
        raise ValueError("GeoJson is niet geldig: %s" % value)


def convert_geojson_to_geometry(value):
    """
    This function converts a geojson to a Shapely.geometry.
    :param value: geojson
    :return: Shapely.geometry
    """
    geojson_element = geojson.loads(json.dumps(value))
    return geometry.shape(geojson_element)


def get_srid_from_geojson(value):
    """
    This function returns the srid of a geojson
    :param value: geojson
    :return: spatial reference identifier (srid)
    """
    if value is None or not value:
        return None
    try:
        if not value.get('crs'):
            return None
        srid = find_srid(value['crs']['properties']['name'])
        # todo make a better implementation for this?! Is there a fixed format in geojson to define CRS

        return srid

    except ValueError:  # pragma NO COVER
        # In deze situatie enkel key en attributeErrors mogelijk
        raise ValueError("Geen geldige Spatial Reference Identifier (SRID) gevonden" % value)


def find_srid(text):
    li = [int(x) for x in re.findall(r'\d+', text) if len(x) in [4, 5]]
    return max(li) if len(li) > 0 else None


def check_within_flanders(geojson_input):
    """
    :param geojson_input: geojson geometrie
    :return: True if the input geojson is within the Flanders region, otherwise False
    """
    if geometry.shape(geojson_input).within(get_flanders_geometry()):
        return True
    return False


def check_in_flanders(geojson_input):
    """
    :param geojson_input: geojson geometrie
    :return: True if the input geojson intersects with Flanders region, otherwise False
    """
    if geometry.shape(geojson_input).intersects(get_flanders_geometry()):
        return True
    return False


def get_flanders_geometry():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(here + '/fixtures/vlaams_gewest.geojson') as geof:
        flanders_features = json.load(geof)
    flanders_geojson = flanders_features['features'][0]['geometry']
    return geometry.shape(flanders_geojson)


def get_centroid_xy(value):
    """
    Returns the centroid x,y of a geojson polygon.
    If the geojson is a multipolygon. It return the centroid of the biggest polygon
    :param value: geojson
    :return: x,y
    """
    geometry_element = convert_geojson_to_geometry(value)
    if geometry_element.type == 'MultiPolygon':
        geometry_element_polygons = list(geometry_element.geoms)
        largest_polygon = max(geometry_element_polygons, key=attrgetter('area'))
        centroid = largest_polygon.centroid.wkt
    else:
        centroid = geometry_element.centroid.wkt
    return ','.join([x for x in re.findall(r'\d+.\d+', centroid)])


def add_crab_ids(crabpy_gateway, address):
    gemeente = address.get("gemeente")
    if gemeente:
        gewest_ids = [2, 1, 3]
        gemeente_val = None
        for gewest_id in gewest_ids:
            gemeenten = crabpy_gateway.list_gemeenten(gewest_id)
            gemeente_val = next((g for g in gemeenten if g.naam.lower() == gemeente.lower()), None)
            if gemeente_val:
                address['gemeente'] = "" + gemeente_val.naam
                address['gemeente_id'] = gemeente_val.id
                break
        straat_naam = address.get("straat")
        if gemeente_val and straat_naam:
            straat_val = next((s for s in gemeente_val.straten if s.label.lower() == straat_naam.lower()), None)
            if straat_val:
                address["straat"] = "" + straat_val.label
                address["straat_id"] = straat_val.id
                huisnummer_naam = address.get("huisnummer")
                if huisnummer_naam:
                    huisnummer_val = next((n for n in straat_val.huisnummers
                                           if n.huisnummer.lower() == huisnummer_naam.lower()), None)
                    if huisnummer_val:
                        address["huisnummer"] = "" + huisnummer_val.huisnummer
                        address["huisnummer_id"] = huisnummer_val.id
        return address


def nearest_location(geojson_element, crabpy_gateway=None):
    """
    Returns the nearest location. If a crabpy_gateway is given, the crab id's will be added to the address.
    Uses the agiv service https://loc.geopunt.be/geolocation/Location?xy=<x,y>
    where <x,y> are the coordinates of the centroid of the geometry (polygon).
    The agiv service returns crab, urbis en poi location types only in Flanders and Brussels.
    :param value: geojson
    :return: - crab address
             - None if the nearest address is nog crab type
    """
    xy = get_centroid_xy(geojson_element)

    r = requests.get('https://loc.geopunt.be/geolocation/Location?xy={0}'.format(xy))
    result = r.json()
    if 'LocationResult' not in result \
            or len(result['LocationResult']) == 0 \
            or 'crab' not in result['LocationResult'][0]['LocationType']:
        return None
    locres = result['LocationResult'][0]['FormattedAddress']
    straat_huisnummer, postcode_gemeente = locres.rsplit(', ', 1)
    straat, huisnummer = straat_huisnummer.rsplit(' ', 1)
    postcode, gemeente = postcode_gemeente.split(' ', 1)
    address = {
        'straat': straat,
        'huisnummer': huisnummer,
        'omschrijving_straat': straat + ', ' + huisnummer,
        'postcode': postcode,
        'gemeente': gemeente,
        'land': 'BE'
    }
    if crabpy_gateway:
        return add_crab_ids(crabpy_gateway, address)
    else:
        return address


class AdminGrenzenClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_admin_objecten(self, geojson_input, admin_grens_type, return_geometry=0):
        """
        This function returns the administrative areas objects which intersects with the input geojson
        :param geojson_input: geojson
        :param admin_grens_type: type of returned administrative objects
        :param return_geometry: boolean indicating whether the geometry of the returned objects should also be included
        :
        :return: list of administrative areas objects
        """
        if check_in_flanders(geojson_input):
            data = {
                'geef_geometrie': return_geometry,
                'type': admin_grens_type,
                'geometrie': geojson_input
            }
            res = requests.post(
                url=self.base_url,
                json=data,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            res.raise_for_status()
            return json.loads(res.text)
        else:
            return []

    def get_gemeenten(self, geojson_input):
        """
        This function returns the names of the municipalities which intersects with the input geojson
        :param geojson_input: geojson
        :return: list of municipalities
        """
        results = self.get_admin_objecten(geojson_input, 'gemeente')
        return [gemeente['naam'] for gemeente in results]

    def get_provincies(self, geojson_input):
        """
        This function returns the names of the provinces which intersects with the input geojson
        :param geojson_input: geojson
        :return: list of municipalities
        """
        results = self.get_admin_objecten(geojson_input, 'provincie')
        return [provincie['naam'] for provincie in results]

    @staticmethod
    def _get_lagest_admin_obj(results, geojson_input):
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return {'niscode': results[0]['id'], 'naam': results[0]['naam']}
        else:
            input_polygon = convert_geojson_to_geometry(geojson_input)
            for result in results:
                admin_geom = convert_geojson_to_geometry(result['geometrie'])
                result['intersection_area'] = admin_geom.intersection(input_polygon).area
            largest_m = max(results, key=lambda x: x['intersection_area'])
            return {'niscode': largest_m['id'], 'naam': largest_m['naam']}

    def get_gemeente(self, geojson_input):
        """
        This function returns the name of the municipality which intersects with the input geojson.
        If more municipalities intersect. The municipality is returned with the largest intersection
        :param value: administratievegrenzen_url
        :param value: geojson
        :return: municipality
        """
        results = self.get_admin_objecten(geojson_input, 'gemeente', 1)
        return self._get_lagest_admin_obj(results, geojson_input)

    def get_provincie(self, geojson_input):
        """
        This function returns the name of the province which intersects with the input geojson.
        If more provinces intersect. The province is returned with the largest intersection.
        :param value: administratievegrenzen_url
        :param value: geojson
        :return: province
        """
        results = self.get_admin_objecten(geojson_input, 'provincie', 1)
        return self._get_lagest_admin_obj(results, geojson_input)
