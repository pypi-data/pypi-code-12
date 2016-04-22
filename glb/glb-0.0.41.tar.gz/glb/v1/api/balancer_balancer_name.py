# -*- coding: utf-8 -*-
from . import Resource
from glb.core.errors import notfounderror
from glb.models.balancer import Balancer as BalancerModel


class BalancerBalancerName(Resource):

    def get(self, balancer_name):
        balancer = BalancerModel.retrieve(balancer_name)
        if balancer:
            return balancer, 200, None
        else:
            return notfounderror()

    def delete(self, balancer_name):
        res = BalancerModel.delete(balancer_name)
        return res, 200, None
