# -*- coding: utf-8 -*-
from flask import g

from . import Resource
from glb.core.errors import notfounderror
from glb.models.balancer import Balancer as BalancerModel


class BalancerBalancerNameEntrypoints(Resource):

    def get(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            return balancer.entrypoints, 200, None
        else:
            return notfounderror()

    def post(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            res = balancer.functions('add_entrypoints')(g.json)
            return res, 201, None
        else:
            return notfounderror()

    def put(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            res = balancer.functions('update_entrypoints')(g.json)
            return res, 200, None
        else:
            return notfounderror()

    def delete(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            domain = g.args.get('domain', '')
            port = g.args.get('port', 0)
            protocol = g.args.get('protocol', None)
            del_type = g.args.get('del_type', 'one')
            if del_type == 'all':
                res = balancer.functions('delete_all_entrypoints')()
            else:
                if port and domain and protocol:
                    res = balancer.functions('delete_one_entrypoint')(domain, port, protocol)
            return res, 200, None
        else:
            return notfounderror()
