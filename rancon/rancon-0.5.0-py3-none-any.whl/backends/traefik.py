from rancon import settings
from . import BackendBase

from urllib.parse import urlparse as up


class TraefikBackend(BackendBase):

    required_opts = ('url',)

    def __init__(self, url, tag=[]):
        parsed_url = up(url)
        items = parsed_url.netloc.split(":")
        # can be a list.
        self.tags = tag if isinstance(tag, list) else [tag]
        self.name_schema = name_schema
        self.id_schema = id_schema
        if len(items) == 1:
            self.consul = consul.Consul(host=parsed_url.netloc,
                                        scheme=parsed_url.scheme)
        else:
            self.consul = consul.Consul(host=items[0], port=items[1],
                                        scheme=parsed_url.scheme)

    def register(self, service):
        svc_id = self._tag_replace(self.id_schema, service)
        svc_name = self._tag_replace(self.name_schema, service)
        success = self.consul.agent.service.register(
            svc_name,
            svc_id,
            address=service.host, port=int(service.port),
            tags=self._get_tags(service),
        )
        if success:
            print("CONSUL: REGISTER: {} using {} / {}"
                  .format(service, svc_name, svc_id))
            return svc_id
        else:
            print("CONSUL: REGISTER: FAILED registering "
                  "service {} using {} / {}"
                  .format(service, svc_name, svc_id))
            return None

    def cleanup(self, keep_services):
        con = self.consul
        check_tag = self._get_cleanup_tag_for(settings.args.id)
        for svc_id, svc in con.agent.services().items():
            if not svc['Tags'] or check_tag not in svc['Tags']:
                continue
            if svc_id not in keep_services:
                print("CONSUL: CLEANUP: de-registering service id {}"
                      .format(svc_id))
                con.agent.service.deregister(svc_id)

    def _get_tags(self, service):
        return [self._tag_replace(x, service) for x in self.tags] + \
               [self._get_cleanup_tag_for(settings.args.id),
                'rancon']


def get():
    return TraefikBackend
