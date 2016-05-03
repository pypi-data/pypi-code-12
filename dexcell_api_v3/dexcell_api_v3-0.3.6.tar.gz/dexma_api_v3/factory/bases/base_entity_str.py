__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType


class BaseEntityStr(Model):

    id = StringType(required=True)
