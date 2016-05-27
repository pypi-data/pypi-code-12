# -*- coding: utf-8 -*-
from flask import g

from . import Resource
from glb.core.errors import notfounderror
from glb.models.balancer import Balancer as BalancerModel, domain_mapping


class BalancerBalancerNameEntrypoints(Resource):

    def get(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            return balancer.entrypoints, 200, None
        else:
            return notfounderror()

    def post(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if not balancer:
            return notfounderror()
        res = balancer.functions('add_entrypoints')(g.json)
        for e in g.json:
            domain = e.get('domain', '')
            d_mapping = domain_mapping.retrieve(domain)
            if not d_mapping:
                obj = dict(domain=domain, balancer_name=balancer_name)
                domain_mapping.save(obj)
                continue
            domain_mapping.update(domain, dict(balancer_name=balancer_name))
        return res, 201, None

    def put(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if not balancer:
            return notfounderror()
        old_domains = set()
        new_domains = set()
        for i in balancer.entrypoints:
            old_domains.add(i['domain'])
        for j in g.json:
            new_domains.add(j['domain'])
        res = balancer.functions('update_entrypoints')(g.json)
        # XXX add domain before delete its duplications
        # cuz duplicate domain in nginx config will cause nginx reload failure
        # but won't cause service interrupt
        for e in g.json:
            domain = e.get('domain', '')
            old_d = domain_mapping.retrieve(domain)
            if not old_d:
                obj = dict(domain=domain, balancer_name=balancer_name)
                domain_mapping.save(obj)
                continue
            domain_mapping.update(domain, dict(balancer_name=balancer_name))
            old_balancer_name = old_d.balancer_name
            if old_balancer_name != balancer_name:
                old_balancer = BalancerModel.retrieve(old_balancer_name)
                port = e.get('port', 0)
                protocol = e.get('protocol', None)
                old_balancer.functions('delete_one_entrypoint')(
                    domain, port, protocol)
        for rd in (old_domains - new_domains):
            domain_mapping.delete(rd)
        return res, 200, None

    def delete(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if not balancer:
            return notfounderror()
        domain = g.args.get('domain', '')
        port = g.args.get('port', 0)
        protocol = g.args.get('protocol', None)
        del_type = g.args.get('del_type', 'one')
        if del_type == 'all':
            res = balancer.functions('delete_all_entrypoints')()
            old_domains = set()
            for i in balancer.entrypoints:
                old_domains.add(i['domain'])
            for d in old_domains:
                domain_mapping.delete(d)
        else:
            if port and domain and protocol:
                res = balancer.functions('delete_one_entrypoint')(
                    domain, port, protocol)
                domain_mapping.delete(domain)
        return res, 200, None
