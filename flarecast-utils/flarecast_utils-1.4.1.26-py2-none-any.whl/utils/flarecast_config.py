import json
from warnings import warn
import requests
import validators


class FlarecastConfig(object):
    __CONFIG_URL = 'https://dev.flarecast.eu/stash/projects/INFRA/repos/' \
                   'dev-infra/browse/global_config.json?&raw'

    def __init__(self, config_path=__CONFIG_URL, auto_load=True):
        self.config_path = config_path
        self.config = {}

        requests.packages.urllib3.disable_warnings()

        # load configuration
        if auto_load:
            if validators.url(config_path):
                self.load_from_url(self.config_path)
            else:
                self.load_from_file(self.config_path)

    def load(self):
        warn("Use 'load_from_url()' to load config file!", DeprecationWarning)
        self.load_from_url(self.config_path)

    def load_from_file(self, config_file):
        with open(config_file, "r") as cfg_file:
            data = cfg_file.readlines()
        self.config = json.loads(data)

    def load_from_url(self, config_url):
        config_resp = requests.get(config_url, verify=False)
        if config_resp.status_code != 200:
            print("Could not load global config file from %s" %
                  self.config_path)
            exit(1)
        self.config = config_resp.json()

    def __getattr__(self, name):
        if not self.config.items():
            raise Exception('Flarecast Config hast not been loaded yet!')

        return self.config.get(name, None)
