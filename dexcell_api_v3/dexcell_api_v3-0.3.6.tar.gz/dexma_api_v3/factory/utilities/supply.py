__author__ = 'dcortes'

from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.location_factory.location_info_factory.country import Country
from dexma_api_v3.factory.location_factory.location_info_factory.address import Address
from info_supply import InfoSupply


class Supply(BaseEntity):

    type = StringType(required=True)
    status = StringType(required=True)
    POD = StringType(required=True)
    name = StringType(required=True)
    store_bills = BooleanType(required=True)
    country = ModelType(Country, required=True)
    address = ModelType(Address)
    info = ModelType(InfoSupply)