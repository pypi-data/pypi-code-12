__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import DecimalType


class Coordinates(Model):

    latitude = DecimalType()
    longitude = DecimalType()