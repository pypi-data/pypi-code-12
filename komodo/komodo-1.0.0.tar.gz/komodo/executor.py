#!/usr/bin/env python
"""
This is where the mainline sits and is responsible for setting up the logging,
the argument parsing and for starting up komodo.
"""

import os
import yaml
import logging
import argparse

from input_algorithms.meta import Meta

from delfick_app import App as DelfickApp

from komodo.datastore import JsonDataStore
from komodo.option_spec.komodo_specs import ConfigRoot
from komodo.server.server import Server

log = logging.getLogger("komodo.executor")

def env_load(loader, node):
    return os.environ[node.value]

class App(DelfickApp):
    cli_categories = ['komodo']
    cli_description = "Application that reads YAML and serves up pretty dashboards"

    def execute(self, cli_args, args_dict, extra_args, logging_handler):
        yaml.add_constructor('!ENV', env_load)
        raw_config = yaml.load(cli_args.config_file)

        # Validate the structure of the config file
        spec = ConfigRoot.FieldSpec()
        config = spec.normalise(Meta(everything=raw_config, path=[]), raw_config)
        config.validate_widgets()

        base_dir = os.path.dirname(cli_args.config_file.name)
        datastore = JsonDataStore(os.path.join(base_dir, "data.json"))

        Server(
              host = cli_args.host
            , port = cli_args.port
            , debug = cli_args.debug
            , datastore=datastore
            , **config
            ).serve()

    def setup_other_logging(self, args, verbose=False, silent=False, debug=False):
        logging.getLogger("requests").setLevel([logging.CRITICAL, logging.ERROR][verbose or debug])

    def specify_other_args(self, parser, defaults):
        parser.add_argument("--config"
            , help = "The config file to read"
            , dest = "config_file"
            , type = argparse.FileType('rb')
            , required = True
            )

        parser.add_argument("--host"
            , help = "The host to serve the dashboards on"
            , dest = "host"
            , default = "localhost"
            )

        parser.add_argument("--port"
            , help = "The port to serve the dashboards on"
            , default = 7546
            , dest = "port"
            , type = int
            )

        return parser

main = App.main
if __name__ == '__main__':
    main()
