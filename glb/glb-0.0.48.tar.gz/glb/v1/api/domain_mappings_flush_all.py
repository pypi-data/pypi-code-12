# -*- coding: utf-8 -*-
from . import Resource
from glb.models.balancer import Balancer as BalancerModel, domain_mapping


def issame_mapping(a, b):
    if a.balancer_name == b.balancer_name and a.domain == b.domain:
        return True
    return False


def minus_mappings(la, lb):
    '''return a - b'''
    res = set()
    for a in la:
        print 'aaaaaa'
        in_lb = False
        for b in lb:
            if issame_mapping(a, b):
                in_lb = True
        if not in_lb:
            res.add(a)
    return res


def get_intersection(la, lb):
    res = set()
    for a in la:
        for b in lb:
            if issame_mapping(a, b):
                res.add(a)
    return res


class DomainMappingsFlushAll(Resource):

    def get(self):
        old_domain_mappings = domain_mapping.retrieve_list()
        balancers = BalancerModel.retrieve_list()
        new_domain_mappings = []
        for b in balancers:
            for e in b.entrypoints:
                objs = [
                    domain_mapping.create(
                        domain=e.get('domain'),
                        balancer_name=b.name)
                    for e in b.entrypoints]
                new_domain_mappings.extend(objs)
        for rd in minus_mappings(old_domain_mappings, new_domain_mappings):
            domain_mapping.delete(rd.domain)
        for nd in minus_mappings(new_domain_mappings, old_domain_mappings):
            domain_mapping.save(
                dict(domain=nd.domain, balancer_name=nd.balancer_name))
        for d in get_intersection(new_domain_mappings, old_domain_mappings):
            domain_mapping.update(
                d.domain, dict(balancer_name=d.balancer_name))
        return None, 200, None
