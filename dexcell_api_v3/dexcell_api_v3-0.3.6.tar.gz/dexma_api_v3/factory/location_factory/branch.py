__author__ = 'dcortes'

from schematics.types import StringType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity # TODO nice path one's moved


class Branch(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)
    parent =  ModelType(BaseEntity, required=True)
