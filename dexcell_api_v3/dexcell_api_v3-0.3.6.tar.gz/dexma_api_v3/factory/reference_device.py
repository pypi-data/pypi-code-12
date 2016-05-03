__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType

from dexma_api_v3.factory.bases.base_entity import BaseEntity


class ReferenceDevice(Model):

    device = ModelType(BaseEntity)
    type = StringType(required=True)