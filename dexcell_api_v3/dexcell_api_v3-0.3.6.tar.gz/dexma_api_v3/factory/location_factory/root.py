__author__ = 'dcortes'

from schematics.types import StringType

from dexma_api_v3.factory.bases.base_entity import BaseEntity


class Root(BaseEntity):

    name = StringType(required=True)
    type = StringType(required=True)

