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
Subcommands for listing information
"""
from ncloud.commands.command import Command
from ncloud.formatting.output import print_table
from ncloud.util.api_call import api_call_json
from ncloud.config import MODELS, DATASETS, RESOURCES


class ListModels(Command):
    @classmethod
    def parser(cls, subparser):
        list_models = subparser.add_parser("list",
                                           help="List all submitted, queued, "
                                                "and running models.")
        list_models_type = list_models.add_mutually_exclusive_group()
        list_models_type.add_argument("--done", action="store_true",
                                      help="Show only models finished "
                                           "training.")
        list_models_type.add_argument("--training", action="store_true",
                                      help="Show only training models.")
        list_models.add_argument("-n", "--count", type=int, default='10',
                                 help="Show up to n most recent models. "
                                      "For unlimited set n=0.")
        list_models_type.add_argument("--details", action="store_true",
                                      help="Show more details about models")

        list_models.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, count=10, details=False, done=False, training=False):
        vals = {"count": count}

        if details:
            vals["details"] = "True"

        if done:
            vals["filter"] = ["Completed", "Error", "Deploying", "Deployed",
                              "Undeploying"]
        elif training:
            vals["filter"] = ["Preparing Data (1/4)", "Preparing Data (2/4)",
                              "Preparing Data (3/4)", "Preparing Data (4/4)",
                              "Queued", "Running"]
        else:
            vals["filter"] = ["Received", "Preparing Data (1/4)",
                              "Preparing Data (2/4)", "Preparing Data (3/4)",
                              "Preparing Data (4/4)", "Submitted", "Queued",
                              "Running", "Removed", "Completed", "Error",
                              "Deploying", "Deployed", "Undeploying"]

        return api_call_json(config, MODELS, params=vals)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['models'])


class DatasetList(Command):
    @classmethod
    def parser(cls, subparser):
        dataset_list = subparser.add_parser("dataset-list",
                                            help="List available datasets.")
        dataset_list.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return api_call_json(config, DATASETS)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['datasets'])


class ResourceList(Command):
    @classmethod
    def parser(cls, subparser):
        list_res = subparser.add_parser("resource-list",
                                        help="List all resources assigned to"
                                             " your tenant.")
        list_res.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return api_call_json(config, RESOURCES)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['resources'])
