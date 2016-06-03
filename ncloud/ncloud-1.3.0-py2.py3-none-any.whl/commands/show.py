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
Subcommands for showing details.
"""
from __future__ import print_function
from builtins import str
import os
import sys
import io
import zipfile
import logging

from ncloud.config import MODELS, DATASETS
from ncloud.util.api_call import api_call, api_call_json
from ncloud.commands.command import Command, string_argument
from ncloud.formatting.time_zone import utc_to_local

logger = logging.getLogger()


class DatasetShow(Command):
    @classmethod
    def parser(cls, subparser):
        dataset_show = subparser.add_parser("dataset-show",
                                            help="Show dataset details for a "
                                                 "given dataset ID.")
        dataset_show.add_argument("dataset_id",
                                  help="ID of dataset to show details of.")
        dataset_show.add_argument("-r", "--rename",
                                  type=string_argument,
                                  help="Rename a dataset.")

        dataset_show.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, dataset_id, rename=None):
        show_path = os.path.join(DATASETS, dataset_id)
        if rename:
            vals = {"operation": "replace", "name": rename}
            res = api_call_json(config, show_path, method="PATCH", data=vals)
        else:
            res = api_call_json(config, show_path)

        for tm in ["created_at", "last_modified"]:
            if tm in res and res[tm] is not None:
                res[tm] = utc_to_local(res[tm])

        return res


class ShowModel(Command):
    @classmethod
    def parser(cls, subparser):
        show_model = subparser.add_parser("show",
                                          help="Show model details for a "
                                               " given model ID.")
        show_model.add_argument("model_id",
                                help="ID of model to show details of.")
        show_model.add_argument("-l", "--console_log", action="store_true",
                                help="Show console log from model runtime.")
        show_model.add_argument("--neon_log", action="store_true",
                                help="Show neon log file.")
        show_model.add_argument("-r", "--rename",
                                type=string_argument,
                                help="Rename a model.")

        show_model.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, console_log=False,
             neon_log=False, rename=None):
        model_id = str(model_id)
        if console_log or neon_log:
            results_path = os.path.join(MODELS, model_id, "results")
            vals = {"format": "zip", "filter": ["*.log"]}
            zipfiles = api_call(config, results_path, params=vals)
            zipbytes = io.BytesIO(zipfiles)
            archive = zipfile.ZipFile(zipbytes)
            ziplogs = archive.namelist()

            # has to be done here because of pytest shenanigans
            # pytest replaces sys.stdout specifically
            write = getattr(sys.stdout, 'buffer', sys.stdout).write
            if neon_log:
                try:
                    write(archive.read('neon.log'))

                except KeyError:
                    logger.warning("attempting to view non-existent neon.log")
            else:
                log = 'launcher.log'
                if log in ziplogs:
                    write(archive.read(log))
        else:
            show_path = os.path.join(MODELS, model_id)
            if rename:
                vals = {"operation": "replace", "name": rename}
                res = api_call_json(config, show_path, method="PATCH",
                                    data=vals)
            else:
                res = api_call_json(config, show_path)

            try:
                fstr = '{0:g}'.format(res['epochs_completed'])
                res['epochs_completed'] = fstr
            except ValueError:
                # prior to helium v1.1.0, we only returned a string
                pass
            for tm in ["train_request", "train_start", "train_end"]:
                if tm in res and res[tm] is not None:
                    res[tm] = utc_to_local(res[tm])
            return res
