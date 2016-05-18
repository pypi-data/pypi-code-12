__author__ = 'zhonghong'

import os
import re
import logging


from zapi.core.utils import load_module, capitalize_name
from zapi.core.input import Input
from zapi.core.load import Loader

log = logging.getLogger(__name__)


class Router(object):

    @classmethod
    def route(cls, app_path, environ):
        if not os.path.exists(os.path.join(app_path, 'controllers')):
            return  "500 Internal Server Error", "Controllers path not found."

        ctrl_classes = load_module(os.path.join(app_path, 'controllers'))
        path = environ['PATH_INFO'].strip()
        if not path:
            ctrl_class_name = 'index.index'
            ctrl_method_name = 'index'
        else:
            path = re.sub(r'/+', '/', path)
            if path == '/':
                ctrl_class_name = 'index.index'
                ctrl_method_name = 'index'
            else:
                if len(path.split('/')) < 3:
                    ctrl_method_name = 'index'
                else:
                    ctrl_method_name = path.split('/')[2]
                ctrl_class_name = "{0}.{0}".format(path.split('/')[1].lower())

        if ctrl_class_name not in ctrl_classes:
            log.info("Controller {0}.{1} Not Found.".format(ctrl_class_name.split('.')[0],
                                                            capitalize_name(ctrl_class_name.split('.')[1])))
            return "404 Not Found", "Controller {0}.{1} Not Found.".format(
                ctrl_class_name.split('.')[0], capitalize_name(ctrl_class_name.split('.')[1])
            )

        ctrl_class = ctrl_classes[ctrl_class_name]
        # inject attributes to the controller
        ctrl_class.input = Input(environ)
        ctrl_class.load = Loader(app_path, ctrl_class)

        ctrl_instance = ctrl_class()
        ctrl_method = getattr(ctrl_instance, ctrl_method_name.lower(), None)
        if not ctrl_method:
            return "404 Not Found", "Method {0}.{1} Not Found.".format(
                ctrl_method_name.lower()
            )

        try:
            ret = ctrl_method()
        except Exception as e:
            return  "500 Internal Server Error", "Exception happened:%s." % e

        return "200 OK", ret