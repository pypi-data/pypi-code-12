# -*- coding: utf-8 -*-

from . import Resource
from glb.models.balancer import Balancer as BalancerModel


class BalancerNamesPostfix(Resource):

    def get(self, postfix):
        all_obj_names = BalancerModel.retrieve_all_obj_ids()
        postfixed_names = [b_name for b_name in all_obj_names
                           if b_name.endswith(postfix)]
        return postfixed_names, 200, None
