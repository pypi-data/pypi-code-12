__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import FloatType, StringType, IntType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.cost_electrical_factory.price_change.tou_change import TOUChange

class multiperiodContractedPeriod(Model):

    price_change = ModelType(TOUChange, default=None, strict=False)
    label = StringType(required=True)
    days_gap = IntType(required=True)
    key = StringType(required=True)
    price = FloatType(required=True)
    val = FloatType(required=True)
    cost = FloatType(required=True)
    contracted_demand = FloatType(required=True)