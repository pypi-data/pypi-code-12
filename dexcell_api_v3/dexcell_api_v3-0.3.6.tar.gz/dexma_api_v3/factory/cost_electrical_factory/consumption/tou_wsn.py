__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType, FloatType
from schematics.types.compound import ListType, ModelType

from dexma_api_v3.factory.cost_electrical_factory.periods.tou_periods import TOUPeriod
from dexma_api_v3.factory.cost_electrical_factory.values.tou_value import TOUValue
from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type


class TOUWSN(Model):

    type = StringType(required=True)
    total_consumption = FloatType(required=True)
    total = FloatType(required=True)
    units = StringType(required=True)

    from_ = DateISO3601Type(required=True, default=None)
    to = DateISO3601Type(required=True)
    periods = ListType(ModelType(TOUPeriod, required=True))
    values = ListType(ModelType(TOUValue, required=True))
