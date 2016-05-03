__author__ = 'dcortes'

from schematics.types import StringType

from dexma_api_v3.factory.bases.base_entity import BaseEntity


class User(BaseEntity):

    username = StringType(required=True)
    role = StringType(required=True)
    locale = StringType(required=True)