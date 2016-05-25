# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Views for Connections tab.
"""

from horizon import exceptions
from horizon import tabs
from horizon.utils import memoized
from horizon_bsn.content.connections import tabs as project_tabs
from openstack_dashboard import api


class IndexView(tabs.TabbedTableView):
    tab_group_class = project_tabs.ConnectionsTabs
    template_name = 'project/connections/index.html'

    @memoized.memoized_method
    def _get_router(self):
        try:
            routers = api.neutron.router_list(
                self.request, **{'tenant_id': self.request.user.project_id})
            router = routers[0] if routers else None
            return router
        except Exception:
            msg = _('Unable to retrieve router for the current tenant.')
            exceptions.handle(self.request, msg)

    @memoized.memoized_method
    def _get_ports(self, router_id):
        try:
            ports = api.neutron.port_list(self.request,
                                          device_id=router_id)
        except Exception:
            ports = []
            msg = _('Unable to retrieve port details.')
            exceptions.handle(self.request, msg)
        return ports

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        router = self._get_router()
        context["router"] = router
        return context

    def get_tabs(self, request, *args, **kwargs):
        router = self._get_router()
        ports = None
        if router:
            request.META['router_id'] = router.id
            ports = self._get_ports(router.id)
        return self.tab_group_class(request, router=router,
                                    ports=ports, **kwargs)
