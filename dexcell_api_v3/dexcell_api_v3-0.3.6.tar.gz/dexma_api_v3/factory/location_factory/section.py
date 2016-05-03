__author__ = 'dcortes'

from schematics.types import StringType, FloatType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.custom_types.unsigned_float_type import UnsignedFloatType


class Section(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)
    parent =  ModelType(BaseEntity, required=True)
    area = UnsignedFloatType()
    summer_temp = FloatType()
    winter_temp = FloatType()
    section_type = StringType(required=True)
