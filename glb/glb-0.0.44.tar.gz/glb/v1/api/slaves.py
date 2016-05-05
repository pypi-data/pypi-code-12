# -*- coding: utf-8 -*-
from . import Resource
from glb.models.slave import Slave as SlaveModel


class Slaves(Resource):

    def get(self):
        slaves = SlaveModel.retrieve_list()
        return slaves, 200, None
