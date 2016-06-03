# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Subcommands for importing models.
"""
from __future__ import print_function
import os
import sys

from ncloud.commands.command import string_argument, Command
from ncloud.util.api_call import api_call_json
from ncloud.util.file_transfer import multipart_upload
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
        if epochs:
            vals["epochs_requested"] = epochs
        if name:
            vals["name"] = name
        if script and os.path.exists(script):
            files = [('script_file', (os.path.basename(script),
                                      open(script, "rb")))]

        def import_model(vals, files):
            return api_call_json(config, MODELS + "import", method="POST",
                                 data=vals, files=files)

        if input.startswith("http") or input.startswith("s3"):
            vals["model_url"] = input
            res = import_model(vals, files)
        elif os.path.exists(input):
            chunksize = 5242880

            basename = os.path.basename(input)

            if os.path.getsize(input) <= chunksize:
                if files is None:
                    files = []
                files.append(('model_file', (basename, open(input, "rb"))))
                res = import_model(vals, files)
            else:
                vals['multipart'] = True
                vals['model_filename'] = basename
                res = import_model(vals, files)
                print("Model ID: {}".format(res['id']))
                multipart_id = res['multipart_id']

                res = multipart_upload(config, input, multipart_id, chunksize)
        else:
            print("no/invalid input model specified")
            sys.exit(1)

        return res

    @staticmethod
    def display_before(conf, args):
        print("importing (may take some time)...")
