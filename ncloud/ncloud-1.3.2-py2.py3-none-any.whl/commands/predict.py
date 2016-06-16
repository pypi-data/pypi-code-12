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
Subcommands for model predictions.
"""
from __future__ import print_function
import os
import sys
import json
from collections import OrderedDict
from ncloud.config import PREDICTIONS, MODELS
from ncloud.util.api_call import api_call, api_call_json
from ncloud.commands.command import Command, print_table


class Deploy(Command):
    @classmethod
    def parser(cls, subparser):
        deploy = subparser.add_parser("deploy",
                                      help="Make a trained model available for"
                                           " generating predictions against.")
        deploy.add_argument("model_id", help="ID of model to deploy.")

        deploy.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id):
        return api_call_json(config, MODELS + model_id + "/deploy",
                             method="POST")


class Undeploy(Command):
    @classmethod
    def parser(cls, subparser):
        undeploy = subparser.add_parser("undeploy",
                                        help="Remove a deployed model.")
        undeploy.add_argument("model_id", help="ID of model to undeploy.")

        undeploy.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id):
        return api_call_json(config, MODELS + model_id + "/deploy",
                             method="DELETE")


class Predict(Command):
    @classmethod
    def parser(cls, subparser):
        predict = subparser.add_parser("predict",
                                       help="Generate predicted outcomes from "
                                            "a deployed model and input data.")
        predict.add_argument("model_id", help="ID of model to to generate "
                                              "predictions against.  Model "
                                              "must be deployed.")
        predict.add_argument("input", help="Input data filename or url to "
                                           " generate predictions for.")
        predict.add_argument("-t", "--in_type", default="image",
                             help="Type of input.  Valid choices are: "
                                  "image (default), json")
        predict.add_argument("-f", "--formatter", default="raw",
                             help="How to format predicted outputs from the "
                                  "network.  Valid choices are: raw (default),"
                                  " classification")
        predict.add_argument("-a", "--args",
                             help="Additional arguments for the formatter. "
                                  "These vary, details can be found at: "
                                  "http://doc.cloud.nervanasys.com "
                                  "(Output Formatters)")

        predict.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, input, model_id, in_type=None, formatter=None, args=None):
        vals = {}
        files = None
        if input.startswith("http") or input.startswith("s3"):
            vals["url"] = input
        elif os.path.exists(input):
            files = [('data', (os.path.basename(input), open(input, "rb")))]
        else:
            print("no/invalid input data specified")
            sys.exit(1)
        if in_type:
            vals["type"] = in_type
        if formatter:
            vals["formatter"] = formatter
        if args:
            vals["args"] = args
        return api_call(config, PREDICTIONS + model_id, method="POST",
                        data=vals, files=files)

    @staticmethod
    def display_after(config, args, res):
        if not args.formatter or args.formatter == "raw":
            print(res)
        else:
            res = json.loads(res, object_pairs_hook=OrderedDict)
            if "predictions" in res:
                print_table(res["predictions"])
            else:
                print_table(res)
