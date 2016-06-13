__author__ = 'zhonghong'

import os

from zapi.core.utils import load_module

class Config(object):

    def __init__(self, app_path):
        self.config_path = os.path.join(app_path, 'config')
        self.configs = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}

        configs = {}
        for k, v in load_module(self.config_path, check_callable=False).iteritems():
            key = k.split('.')[-1]
            configs[key] = v

        return configs

    def __getattr__(self, item):
        if item in self.configs:
            return self.configs[item]

        return None


if __name__ == '__main__':
    config = Config('E:/python_project/tmp-dev/codesnippet/zapi/application')
    print config.db.get('db')

