#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import, unicode_literals
from .enum import Enum


class EnumField(serializers.ChoiceField):
    pass

