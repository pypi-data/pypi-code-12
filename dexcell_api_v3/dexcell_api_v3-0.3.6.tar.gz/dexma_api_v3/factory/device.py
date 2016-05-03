__author__ = 'dcortes'

from schematics.types import StringType
from schematics.types.compound import ModelType

from datasource import DataSource
from dexma_api_v3.factory.bases.base_entity import BaseEntity


class Device(BaseEntity):

    name = StringType(required=True)
    local_id = StringType(required=True)
    datasource = ModelType(DataSource, required=True)
    status = StringType(required=True)