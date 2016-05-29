# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from .api.balancer_balancer_name_frontend import BalancerBalancerNameFrontend
from .api.domain_mappings import DomainMappings
from .api.balancer_balancer_name_backends import BalancerBalancerNameBackends
from .api.balancer_balancer_name_entrypoints import BalancerBalancerNameEntrypoints
from .api.balancer import Balancer
from .api.balancer_balancer_name import BalancerBalancerName
from .api.slaves import Slaves
from .api.domain_mappings_flush_all import DomainMappingsFlushAll
from .api.balancer_names_postfix import BalancerNamesPostfix


routes = [
    dict(resource=BalancerBalancerNameFrontend, urls=['/balancer/<balancer_name>/frontend'], endpoint='balancer_balancer_name_frontend'),
    dict(resource=DomainMappings, urls=['/domain_mappings'], endpoint='domain_mappings'),
    dict(resource=BalancerBalancerNameBackends, urls=['/balancer/<balancer_name>/backends'], endpoint='balancer_balancer_name_backends'),
    dict(resource=BalancerBalancerNameEntrypoints, urls=['/balancer/<balancer_name>/entrypoints'], endpoint='balancer_balancer_name_entrypoints'),
    dict(resource=Balancer, urls=['/balancer'], endpoint='balancer'),
    dict(resource=BalancerBalancerName, urls=['/balancer/<balancer_name>'], endpoint='balancer_balancer_name'),
    dict(resource=Slaves, urls=['/slaves'], endpoint='slaves'),
    dict(resource=DomainMappingsFlushAll, urls=['/domain_mappings/flush_all'], endpoint='domain_mappings_flush_all'),
    dict(resource=BalancerNamesPostfix, urls=['/balancer/names/<postfix>'], endpoint='balancer_names_postfix'),
]