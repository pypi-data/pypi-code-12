__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import IntType

from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type #TODO to change to relative path when created library


class Value(Model):

    v = IntType(required=True)
    ts = DateISO3601Type(required=True)