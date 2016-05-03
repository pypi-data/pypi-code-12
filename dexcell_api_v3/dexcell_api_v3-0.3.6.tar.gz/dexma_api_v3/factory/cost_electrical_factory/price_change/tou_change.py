__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType

from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type


class TOUChange(Model):

    key = StringType(required=True)
    from_ = DateISO3601Type(required=True, default=None)