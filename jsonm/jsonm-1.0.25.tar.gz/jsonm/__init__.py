# -*- coding: utf-8 -*-

__version__ = '1.0.25'

from .application import Application
from .fields import BaseField, Field
from .model import Model
from .vals import default_app

# 指向默认的
json_dumps = default_app.json_dumps
json_loads = default_app.json_loads
register_models = default_app.register_models
