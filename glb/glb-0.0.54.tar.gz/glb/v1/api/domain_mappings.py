# -*- coding: utf-8 -*-
from . import Resource
from glb.models.balancer import domain_mapping


class DomainMappings(Resource):

    def get(self):
        domain_mappings = domain_mapping.retrieve_list()
        return domain_mappings, 200, None
