__author__ = 'dcortes'

from schematics.types import StringType, FloatType
from schematics.types.compound import ListType, ModelType

from dexma_api_v3.factory.reference_device import ReferenceDevice
from dexma_api_v3.factory.location_factory.location_info_factory.address import Address
from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.custom_types.unsigned_float_type import UnsignedFloatType


class Leaf(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)
    parent =  ModelType(BaseEntity, required=True)
    area = UnsignedFloatType() # now required but as some locations can still not have it we will let it be as it
    summer_temp = FloatType()
    winter_temp = FloatType()
    activity = StringType(required=True)
    reference_devices = ListType(ModelType(ReferenceDevice, required=True))
    address = ModelType(Address) # now required but as some locations can still not have it we will let it be as it
