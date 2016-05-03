__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType

from dexma_api_v3.factory.bases.base_entity import BaseEntity
from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type
from dexma_api_v3.factory.user import User


class Session(Model):

    account = ModelType(BaseEntity, required=True)
    current_location = ModelType(BaseEntity, required=True)
    locations_below = ListType(ModelType(BaseEntity), required=True)
    location_tags = ListType(StringType, required=True, default=[])
    current_time = DateISO3601Type(required=True)
    user = ModelType(User, required=True)
