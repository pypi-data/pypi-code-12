import os
import yaml


def init_config():
    config = "#Config in yml format\nwl_access_token:'YOUR_WUNDERLIST_ACCESSTOKEN'\n"
    user_path = os.path.expanduser("~")
    gito_config = os.path.join(user_path, ".gito")
    if os.path.exists(gito_config):
        print "Gito Configuration already exists - ", gito_config
    else:
        file = open(gito_config, "w")
        file.write(config)
        file.close()
        print "Gito Configuration created - " + gito_config


class Config:
    def __init__(self):
        self.user_path = os.path.expanduser("~")
        self.gito_config = os.path.join(self.user_path, ".gito")

    def get_config(self):
        with open(self.gito_config, "r") as stream:
            return yaml.load(stream)

    def config_exists(self):
        return True if os.path.exists(self.gito_config) else False