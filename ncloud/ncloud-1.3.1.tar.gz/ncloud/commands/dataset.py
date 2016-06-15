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
Subcommands for working with datasets.
"""
from __future__ import print_function
from builtins import str

import os
import queue

from ncloud.commands.command import Command
from ncloud.util.api_call import api_call, api_call_json
from ncloud.config import DATASETS
from ncloud.util.file_transfer import parallel_upload, upload_file


class DatasetUpload(Command):
    @classmethod
    def parser(cls, subparser):
        dataset_upload = subparser.add_parser("dataset-upload",
                                              help="Upload a custom dataset "
                                                   "to Nervana Cloud.")
        dataset_upload.add_argument("directory",
                                    help="Directory path of the data. Uploads "
                                         "all visible files recursively.")
        dataset_upload.add_argument("-n", "--name",
                                    help="Colloquial name of the dataset. "
                                         "Default name will be given if not "
                                         "provided.")
        dataset_upload.add_argument("--raw", action="store_true",
                                    help="Skip cloud data processing, "
                                         "upload raw (or already processed) "
                                         "data.")
        dataset_upload.add_argument("-i", "--dataset_id", default=None,
                                    type=str,
                                    help="Add data to an existing dataset "
                                         "with this id.  This will replace "
                                         "identically-named files.")

        dataset_upload.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, directory, name=None, raw=False, dataset_id=None):
        vals = {}
        if name:
            vals["name"] = name

        if raw:
            vals["preprocess"] = False

        if dataset_id is None:
            create_dataset = api_call_json(config, DATASETS, method="POST",
                                           data=vals)
            if "id" not in create_dataset:
                print("Could not create dataset.")
                return

            dataset_id = str(create_dataset["id"])
            print("Created dataset with ID {}.".format(dataset_id))

        upload_queue = queue.Queue()

        if os.path.isdir(directory):
            total_files = len([f for _, _, filelist in os.walk(directory)
                               for f in filelist if f[0] != '.'])
            for dirpath, _, filenames in os.walk(directory):
                filenames = [f for f in filenames if f[0] != '.']
                reldir = os.path.relpath(dirpath, directory)
                reldir = reldir if reldir != "." else ""
                for filename in filenames:
                    relfile = os.path.join(reldir, filename)
                    filepath = os.path.join(directory, relfile)
                    upload_queue.put((dataset_id, relfile, filepath))

            success, failed = parallel_upload(config, upload_queue,
                                              total_files)
        else:
            total_files = 1
            success, failed = 0, 0
            filename = os.path.basename(directory)
            try:
                upload_file(config, dataset_id, filename, directory)
                success = 1
            except SystemExit:
                failed = 1
        output = {"id": dataset_id, "success": success, "failed": failed,
                  "total_files": total_files}
        return output


class DatasetLink(Command):
    @classmethod
    def parser(cls, subparser):
        dataset_link = subparser.add_parser("dataset-link",
                                            help="Link a dataset not residing "
                                                 "in the Nervana Cloud.")
        dataset_link.add_argument("directory",
                                  help="Network path of the data root "
                                       "directory.")
        dataset_link.add_argument("-n", "--name",
                                  help="Colloquial name of the dataset. "
                                       "Default name will be given if not "
                                       "provided.")
        dataset_link.add_argument("--raw", action="store_true",
                                  help="Skip cloud data processing, upload "
                                       "raw (or already processed) data.")

        dataset_link.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, directory, name=None, raw=False):
        vals = {"location_path": directory}
        if raw:
            vals["preprocess"] = False

        if name:
            vals["name"] = name

        res = api_call_json(config, DATASETS, method="POST", data=vals)
        return res

    @staticmethod
    def display_after(config, args, res):
        pass


class DatasetRemove(Command):
    @classmethod
    def parser(cls, subparser):
        dataset_remove = subparser.add_parser("dataset-remove",
                                              help="Remove a linked or "
                                                   "uploaded dataset.")
        dataset_remove.add_argument("dataset_id",
                                    help="ID of dataset to remove.")

        dataset_remove.set_defaults(func=cls.arg_call)

    @staticmethod
    def arg_names():
        return ['dataset_id']

    @staticmethod
    def call(config, dataset_id):
        res = api_call(config, DATASETS + dataset_id, method="DELETE")
        return res

    @staticmethod
    def display_after(config, args, res):
        pass
