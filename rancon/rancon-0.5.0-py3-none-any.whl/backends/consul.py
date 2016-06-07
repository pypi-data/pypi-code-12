from rancon import settings
from rancon.tools import tag_replace
from . import BackendBase

import consul

from urllib.parse import urlparse as up


class ConsulBackend(BackendBase):

    required_opts = ('url',)
    additional_opts = ('id_schema',)

    def __init__(self, url, tag=[],
                 id_schema='%NAME%_%HOST%_%PORT%'):
        parsed_url = up(url)
        items = parsed_url.netloc.split(":")
        # can be a list.
        self.tags = tag if isinstance(tag, list) else [tag]
        self.id_schema = id_schema
        if len(items) == 1:
            self.consul = consul.Consul(host=parsed_url.netloc,
                                        scheme=parsed_url.scheme)
        else:
            self.consul = consul.Consul(host=items[0], port=items[1],
                                        scheme=parsed_url.scheme)

    def register(self, service):
        svc_id = tag_replace(self.id_schema, service)
        success = self.consul.agent.service.register(
            service.name,
            svc_id,
            address=service.host, port=int(service.port),
            tags=self._get_tags(service),
        )
        if success:
            print("CONSUL: REGISTER: {} using {} / {}"
                  .format(service, service.name, svc_id))
            return svc_id
        else:
            print("CONSUL: REGISTER: FAILED registering "
                  "service {} using {} / {}"
                  .format(service, service.name, svc_id))
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
        tag_list_str = service.get('tag', '')
        tag_list = tag_list_str.split(",") if tag_list_str else []
        tmp =  [tag_replace(x, service).strip() for x in tag_list] + \
               [self._get_cleanup_tag_for(settings.args.id),
                'rancon']
        return tmp


def get():
    return ConsulBackend
