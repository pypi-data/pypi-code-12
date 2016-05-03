__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.location_factory.location_info_factory.country import Country
from coordinates import Coordinates


class Address(Model):

    street = StringType()
    zip = StringType()
    city = StringType()
    country = ModelType(Country)
    coordinates = ModelType(Coordinates)