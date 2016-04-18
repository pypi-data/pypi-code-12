# coding=utf-8
#
# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""BIG-IP® Local Traffic Manager™ (LTM®) module.

REST URI
    ``http://localhost/mgmt/tm/ltm/``

GUI Path
    ``Local Traffic``

REST Kind
    ``tm:ltm:*``
"""


from f5.bigip.ltm.monitor import Monitor
from f5.bigip.ltm.nat import Nats
from f5.bigip.ltm.node import Nodes
from f5.bigip.ltm.persistence import Persistences
from f5.bigip.ltm.policy import Policys
from f5.bigip.ltm.pool import Pools
from f5.bigip.ltm.rule import Rules
from f5.bigip.ltm.snat import Snats
from f5.bigip.ltm.snat_translation import Snat_Translations
from f5.bigip.ltm.snatpool import Snatpools
from f5.bigip.ltm.virtual import Virtuals
from f5.bigip.ltm.virtual_address import Virtual_Address_s
from f5.bigip.resource import OrganizingCollection


class Ltm(OrganizingCollection):
    """BIG-IP® Local Traffic Manager (LTM) organizing collection."""
    def __init__(self, bigip):
        super(Ltm, self).__init__(bigip)
        self._meta_data['allowed_lazy_attributes'] = [
            Monitor,
            Nats,
            Nodes,
            Persistences,
            Policys,
            Pools,
            Rules,
            Snats,
            Snatpools,
            Snat_Translations,
            Virtuals,
            Virtual_Address_s,
        ]
