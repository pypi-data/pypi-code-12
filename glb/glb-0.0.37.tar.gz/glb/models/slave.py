# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .base import Model


class Slave(Model):

    __prefix_key__ = 'glb:slaves'
    __primary_key__ = 'address'
    __schema_default__ = {
        'address': ''
    }
