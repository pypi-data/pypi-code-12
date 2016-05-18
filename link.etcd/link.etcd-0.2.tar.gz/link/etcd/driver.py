# -*- coding: utf-8 -*-

from b3j0f.conf.driver.base import ConfDriver
from b3j0f.conf.model.param import Parameter

from link.etcd.middleware import EtcdMiddleware


class EtcdConfDriver(ConfDriver):
    """
    Driver that reads configuration from **etcd**.
    """

    def __init__(self, *args, **kwargs):
        super(EtcdConfDriver, self).__init__(*args, **kwargs)

        self.client = EtcdMiddleware()

    def __del__(self):
        self.client.disconnect()

    def rscpaths(self, path):
        return [path]

    def resource(self):
        return {}

    def _pathresource(self, rscpath):
        return self.client[rscpath]

    def _cnames(self, resource):
        return resource.keys()

    def _params(self, resource, cname):
        params = resource[cname]

        return [
            Parameter(name=key, svalue=params[key]) for key in params
        ]

    def _setconf(self, conf, resource, rscpath):
        for category in conf.values():
            cat = resource.setdefault(category.name, {})

            for parameter in category.values():
                cat[parameter.name] = parameter.svalue

        self.client[rscpath] = resource
