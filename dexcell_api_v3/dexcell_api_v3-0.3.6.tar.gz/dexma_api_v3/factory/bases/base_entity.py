__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import LongType


class BaseEntity(Model):

    id = LongType(required=True)
