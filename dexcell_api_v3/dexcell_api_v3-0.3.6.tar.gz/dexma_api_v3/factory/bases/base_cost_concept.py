__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType


class BaseCostConcept(Model):

    type = StringType(required=True)
