__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import FloatType, StringType

from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type


class TOUValue(Model):

    k = StringType(required=True)
    v = FloatType(required=True)
    c = FloatType(required=True)
    ts = DateISO3601Type(required=True)