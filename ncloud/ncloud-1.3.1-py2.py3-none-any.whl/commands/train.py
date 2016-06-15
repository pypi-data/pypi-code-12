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
Subcommands for training a model
"""
import os
import logging
from ncloud.commands.command import string_argument, Command
from ncloud.util.api_call import api_call_json
from ncloud.config import MODELS

logger = logging.getLogger()


class TrainModel(Command):
    @classmethod
    def parser(cls, subparser):
        train = subparser.add_parser("train",
                                     help="Submit a deep learning model for "
                                          "training.")
        train.add_argument("filename",
                           type=string_argument,
                           help=".yaml or .py script file for Neon to "
                                "execute.")
        train.add_argument("-n", "--name",
                           type=string_argument,
                           help="Colloquial name of the model. Default"
                                " name will be given if not provided.")
        train.add_argument("-d", "--dataset_id",
                           help="ID of dataset to use.")
        train.add_argument("-v", "--validation_percent", default=.2,
                           help="Percent of dataset to use as validation "
                                "split.")
        train.add_argument("-e", "--epochs",
                           help="Number of epochs to train this model.")
        train.add_argument("-z", "--batch_size",
                           help="Mini-batch size to train this model.")
        train.add_argument("--framework_version",
                           help="Neon tag, branch or commit to use.")
        train.add_argument("--mgpu_version",
                           help="MGPU tag, branch or commit to use, if "
                                "'gpus' > 1.")
        train.add_argument("--args", help="Neon command line arguments.")
        train.add_argument("--resume_model_id",
                           help="Start training a new model using the state "
                                "parameters of a previous one.")
        train.add_argument("-g", "--gpus", default=1,
                           help="Number of GPUs to train this model with.")
        train.add_argument("-r", "--replicas", default=0,
                           help="Number of replicas of the main process to "
                                "invoke.  0 means use standard process, 1 "
                                "means use a parameter server, 2-N means "
                                "use peer-to-peer communication.")
        train.add_argument("--custom_code_url",
                           help="URL for codebase containing custom neon "
                                "scripts and extensions.")
        train.add_argument("--custom_code_commit", default="master",
                           help="Commit ID or branch specifier for custom "
                                "code repo.")

        train.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, filename, gpus=1, replicas=0, framework_version=None,
             mgpu_version=None, name=None, dataset_id=None,
             validation_percent=None, custom_code_url=None,
             args=None, resume_model_id=None, epochs=10, batch_size=128,
             custom_code_commit=None):

        vals = {"filename": filename, "gpus": gpus,
                "replicas": replicas}
        extension = os.path.splitext(filename)[1][1:]
        if extension in ["yaml", "py"]:
            if not custom_code_url:
                with open(filename, "r") as model_file:
                    model_data = model_file.read()
                    vals[extension] = model_data

        if framework_version:
            vals["framework_version"] = framework_version

        if mgpu_version:
            vals["mgpu_version"] = mgpu_version

        if name:
            vals["name"] = name

        if dataset_id:
            vals["dataset_id"] = dataset_id
            assert validation_percent is not None
            vals["validation_percent"] = validation_percent

        if args:
            vals["args"] = args

        if resume_model_id:
            vals["resume_model_id"] = resume_model_id

        if epochs:
            vals["epochs"] = epochs

        if batch_size:
            vals["batch_size"] = batch_size

        if custom_code_url:
            vals["custom_code_url"] = custom_code_url
            vals["custom_code_cmd"] = filename

        if custom_code_commit:
            vals["custom_code_commit"] = custom_code_commit

        return api_call_json(config, MODELS, method="POST", data=vals)


class StopTraining(Command):
    @classmethod
    def parser(cls, subparser):
        stop_training = subparser.add_parser("stop",
                                             help="Stop training a model "
                                             " given a model ID.")
        stop_training.add_argument("model_id", help="ID of model to stop.")
        stop_training.set_defaults(func=cls.arg_call)

    @staticmethod
    def arg_names():
        return ['model_id']

    @staticmethod
    def call(config, model_id):
        return api_call_json(config, MODELS + model_id, method="DELETE")
