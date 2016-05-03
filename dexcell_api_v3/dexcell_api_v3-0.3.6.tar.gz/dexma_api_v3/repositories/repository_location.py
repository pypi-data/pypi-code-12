__author__ = 'dcortes'

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_location import GatewayLocation
from dexma_api_v3.factory.location_factory.branch import Branch
from dexma_api_v3.factory.location_factory.leaf import Leaf
from dexma_api_v3.factory.location_factory.root import Root
from dexma_api_v3.factory.location_factory.section import Section


class RepositoryLocation(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayLocation(endpoint)

    def wrapper_location(self, location_dict):
        if "type" not in location_dict:
            raise Exception("undefined type of location")
        elif location_dict["type"] == "ROOT":
            location = Root(location_dict)
        elif location_dict["type"] == "BRANCH":
            location = Branch(location_dict)
        elif location_dict["type"] == "LEAF":
            location = Leaf(location_dict)
        elif location_dict["type"] == "SECTION":
            location = Section(location_dict)
        else:
            raise Exception("type {} not allowed".format(location_dict["type"]))
        location.validate()
        return location

    def get(self, token, id):
        location_dict = self.gateway.get(token, id)
        return self.wrapper_location(location_dict)

    def fetch(self, token, parameters=None):
        locations_dict = self.gateway.fetch(token, parameters)
        return [self.wrapper_location(loc) for loc in locations_dict]

    def save(self, token, location):
        status = self.gateway.save(token, location)
        return status