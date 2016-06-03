# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for importing models.
"""
from __future__ import print_function
import os
import sys
from ncloud.commands.command import string_argument, Command
from ncloud.util.api_call import api_call_json
from ncloud.config import MODELS


class ImportModel(Command):
    @classmethod
    def parser(cls, subparser):
        i_pars = subparser.add_parser("import",
                                      help="Import a previously trained "
                                           "model.")
        i_pars.add_argument("input",
                            help="Serialized neon model filename or url "
                                 "to import.")
        i_pars.add_argument("-s", "--script",
                            help=".py or .yaml script used to train the "
                                 "imported model.")
        i_pars.add_argument("-e", "--epochs",
                            help="Number of epochs imported model trained. "
                                 "(amount originally requested)")
        i_pars.add_argument("-n", "--name", type=string_argument,
                            help="Colloquial name of the model. Default "
                                 "name will be given if not provided.")

        i_pars.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, input, epochs=None, name=None, script=None):
        vals = dict()
        files = None
        if input.startswith("http") or input.startswith("s3"):
            vals["model_url"] = input
        elif os.path.exists(input):
            files = [('model_file', (os.path.basename(input),
                                     open(input, "rb")))]
        else:
            print("no/invalid input model specified")
            sys.exit(1)
        if epochs:
            vals["epochs_requested"] = epochs
        if name:
            vals["name"] = name
        if script and os.path.exists(script):
            if files is None:
                files = []
            files.append(('script_file', (os.path.basename(script),
                                          open(script, "rb"))))
        res = api_call_json(config, MODELS + "import", method="POST",
                            data=vals, files=files)
        return res

    @staticmethod
    def display_before(conf, args):
        print("importing (may take some time)...")
