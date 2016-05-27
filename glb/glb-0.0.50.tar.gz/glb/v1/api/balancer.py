# -*- coding: utf-8 -*-
from flask import g

from . import Resource
from glb.models.balancer import Balancer as BalancerModel


class Balancer(Resource):

    def get(self):
        balancers = BalancerModel.retrieve_list()
        return balancers, 200, None

    def post(self):
        res = BalancerModel.save_balancer(g.json)
        return res, 201, None
