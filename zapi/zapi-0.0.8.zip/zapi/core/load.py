__author__ = 'zhonghong'

import os

from zapi.core.common import Common
from zapi.core.utils import load_module
from zapi.core.exceptions import ModelNotFound

class Loader(Common):

    def __init__(self, app_path, obj):
        super(Loader, self).__init__(app_path)
        self.app_path = app_path
        self.obj = obj

    def model(self, model, alias=None):
        model_classes = load_module(os.path.join(self.app_path, 'models'))
        model_class_name = "{0}.{0}".format(model.lower())

        if model_class_name not in model_classes:
            raise ModelNotFound(model=model)

        model_class = model_classes[model_class_name]
        # add db handler to the model class
        setattr(model_class, 'db', self._get_db_handler)

        model_instance = model_class()
        setattr(self.obj, model, model_instance)
        if alias:
            setattr(self.obj, alias, model_instance)

    def config(self):
        setattr(self.obj, 'config', self._get_config)

