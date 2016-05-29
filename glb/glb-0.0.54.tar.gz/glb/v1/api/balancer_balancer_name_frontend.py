# -*- coding: utf-8 -*-
from flask import g

from . import Resource
from glb.core.errors import notfounderror
from glb.models.balancer import Balancer as BalancerModel


class BalancerBalancerNameFrontend(Resource):

    def get(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            return balancer.frontend, 200, None
        else:
            return notfounderror()

    def put(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            res = balancer.functions('update_frontend')(g.json)
            return res, 200, None
        else:
            return notfounderror()
