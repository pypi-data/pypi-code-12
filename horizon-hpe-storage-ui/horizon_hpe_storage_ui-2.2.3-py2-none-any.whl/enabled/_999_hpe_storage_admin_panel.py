# (c) Copyright [2015] Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# The name of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'hpe_storage'
# The name of the dashboard the PANEL is associated with. Required.
PANEL_DASHBOARD = 'admin'
# The name of the panel group the PANEL is associated with.
PANEL_GROUP = 'admin'

# Python panel class of the PANEL to be added.
ADD_PANEL = 'horizon_hpe_storage.storage_panel.panel.HPEStorage'

ADD_INSTALLED_APPS = ['horizon_hpe_storage.storage_panel']

# override default behavior for admin->volumes
UPDATE_HORIZON_CONFIG = { 'customization_module': 'horizon_hpe_storage.overrides', }

