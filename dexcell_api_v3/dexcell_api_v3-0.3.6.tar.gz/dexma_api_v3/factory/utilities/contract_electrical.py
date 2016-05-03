__author__ = 'dcortes'

from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.bases.base_entity_str import BaseEntityStr
from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type
from dexma_api_v3.factory.utilities.prices_config import PricesConfig


class ContractElectrical(BaseEntity):

    type = StringType(required=True)
    name = StringType(required=True)
    from_ = DateISO3601Type(required=True)
    to = DateISO3601Type(required=True)
    currency = StringType(required=True)
    simulation = BooleanType(required=True)
    prices = ModelType(BaseEntityStr, required=True)
    supply = ModelType(BaseEntityStr, required=True)
    prices_config = ModelType(PricesConfig, required=True)
    currency_symbol = StringType(required=True)