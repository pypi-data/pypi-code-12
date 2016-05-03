__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import IntType


class DataSource(Model):

    id = IntType(required=True)