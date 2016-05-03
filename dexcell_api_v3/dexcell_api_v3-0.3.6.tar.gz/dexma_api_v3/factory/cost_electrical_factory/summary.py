__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType, PolyModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.bases.base_entity_str import BaseEntityStr
from dexma_api_v3.factory.device import Device
from dexma_api_v3.factory.utilities.price_electrical import PriceElectrical
from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type


def claim_device(field, data):
  return None if not isinstance(data, dict) else Device if 'name' in data else BaseEntity


def claim_price(field, data):
  return None if not isinstance(data, dict) else PriceElectrical if 'type' in data else BaseEntityStr


class Summary(Model):

    tz = StringType(required=True)
    to = DateISO3601Type(required=True)
    from_ = DateISO3601Type(required=True)
    contract = ModelType(BaseEntity, required=True)
    account = ModelType(BaseEntity, required=True)
    device = PolyModelType(BaseEntity, claim_function=claim_device)
    prices = PolyModelType(BaseEntityStr, claim_function=claim_price)
    supply = ModelType(BaseEntity, required=True)
