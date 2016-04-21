# -*- coding: utf-8 -*-
from flask import g

from . import Resource
from glb.core.errors import notfounderror
from glb.models.balancer import Balancer as BalancerModel


class BalancerBalancerNameBackends(Resource):

    def get(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            return balancer.backends, 200, None
        else:
            return notfounderror()

    def post(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            res = balancer.functions('add_backends')(g.json)
            return res, 201, None
        else:
            return notfounderror()

    def put(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            res = balancer.functions('update_backends')(g.json)
            return res, 200, None
        else:
            return notfounderror

    def delete(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            cid = g.args.get('cid', None)
            addr = g.args.get('address', '')
            port = int(g.args.get('port', 0))
            tag = g.args.get('tag', None)
            res = False
            if cid:
                res = balancer.functions('delete_backend_by_cid')(cid)
            if addr and port:
                res = balancer.functions('delete_backend_by_addr_port')(addr, port)
            if tag:
                res = balancer.functions('delete_backend_by_tag')(tag)
            return res, 200, None
        else:
            return notfounderror
