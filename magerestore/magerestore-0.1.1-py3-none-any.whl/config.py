import json


class Config:

    def __init__(self):
        self.repos = {}
        self.resources = {}

    def from_json(self, filename):
        with open(filename) as json_file:
            json_dict = json.load(json_file)

        return self.from_dict(json_dict)

    def from_dict(self, config_dict):
        self.repos = config_dict['repositories']
        self.resources = config_dict['resources']
