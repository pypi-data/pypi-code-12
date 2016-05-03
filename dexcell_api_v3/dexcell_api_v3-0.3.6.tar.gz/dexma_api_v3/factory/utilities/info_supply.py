__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType


class InfoSupply(Model):

    alias = StringType()
    meter_number = StringType()
    distributor = StringType()
    register_date = StringType()
    commissioning_date = StringType()
    description = StringType()
    comments = StringType()
