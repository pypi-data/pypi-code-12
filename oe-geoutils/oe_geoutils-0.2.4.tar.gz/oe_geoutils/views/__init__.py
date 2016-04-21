# -*- coding: utf-8 -*-
from pyramid.view import view_defaults, view_config
from oe_geoutils.utils import check_in_flanders, check_within_flanders, nearest_location
from pyramid.httpexceptions import HTTPBadRequest
import colander


class ValidationFailure(Exception):
    '''
    Custom Exception for data validation errors.
    '''

    def __init__(self, msg, errors):
        self.msg = msg
        self.errors = errors


@view_defaults(renderer='json', accept='application/json')
class View(object):
    def __init__(self, request):
        self.request = request
        self.request_LOCALE_ = 'nl'

    def _retrieve_json(self):
        if self.request.body and not self.request.body == '':
            return self.request.json_body
        else:
            raise HTTPBadRequest("request has no body")

    def validate_geojson(self, params):
        max_area = self.request.registry.settings.get('oe_geoutils.max_area', 8000)
        from oe_geoutils.validation.validators_contour import (
            GeometrieSchemaNode as geometrie_schema
        )
        try:
            return geometrie_schema(max_area).deserialize(params)
        except colander.Invalid as e:
            raise ValidationFailure(
                    'De geojson geometrie is niet geldig.',
                    e.asdict(translate=self.request.localizer.translate)
            )

    @view_config(route_name='nearest_address')
    def nearest_address(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        if check_in_flanders(geojson_input):
            crab_gateway = self.request.crab_gateway() if hasattr(self.request, 'crab_gateway') else None
            address = nearest_location(geojson_input, crab_gateway)
            if address is None:
                return {"found": False}
            return {"found": True, "address": address}
        else:
            raise ValidationFailure(
                    "De geojson geometrie is niet geldig.",
                    {"": "Geometrie ligt niet binnen Vlaanderen"}
            )

    @view_config(route_name='check_in_flanders')
    def check_in_flanders(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return {'IntersectFlanders': check_in_flanders(geojson_input)}

    @view_config(route_name='check_within_flanders')
    def check_within_flanders(self):
        data = self._retrieve_json()
        geojson_input = self.validate_geojson(data)
        return {'WithinFlanders': check_within_flanders(geojson_input)}
