from . import SourceBase
from rancon.service import Service

from cattleprod import poke
from dotmap import DotMap


class RancherSource(SourceBase):

    required_opts = ('url',)
    additional_opts = ('accesskey', 'secretkey', 'default_name_scheme')

    def __init__(self, url, accesskey=None, secretkey=None,
                 default_name_scheme='%NAME%'):
        self.url = url
        self.access = accesskey
        self.secret = secretkey
        self.default_name_scheme = default_name_scheme
        self.cache = DotMap()

    def get_services(self, **_):
        starting_point = poke(self.url)
        rv = []
        services = []
        # get all services with rancon(\..+) labels
        for service in starting_point.get_services():
            labels = service.data.fields.launchConfig.labels
            for label in labels:
                if label == 'rancon' or label.startswith("rancon."):
                    services.append(service)
                    break
            else:
                continue
        # create service instances
        for service in services:
            endpoints = service.data.fields.publicEndpoints
            labels = service.data.fields.launchConfig.labels
            for endpoint in endpoints:
                meta = {k.split(".", 1)[1].replace(".", "_"): v
                        for k, v in labels.items()
                        if k.startswith('rancon.')}
                meta['host'] = endpoint['ipAddress']
                meta['port'] = endpoint['port']
                meta['service'] = service.name
                meta['stack'] = self._get_name_for(service.links.environment)
                meta['environment'] = self._get_name_for(service.links.account)
                if 'name' not in meta:
                    meta['name'] = service.name
                svc = Service(source=service, **meta)
                rv.append(svc)
        # return service instances
        return rv

    def _get_name_for(self, url):
        if not self.cache[url]:
            self.cache[url] = poke(url).name
        return self.cache[url]


def get():
    return RancherSource
