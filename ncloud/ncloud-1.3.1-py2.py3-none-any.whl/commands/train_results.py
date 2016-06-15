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
Subcommands for getting training results.
"""
from __future__ import print_function
import os
from datetime import datetime
import requests
from ncloud.commands.command import Command
from ncloud.util.api_call import api_call, api_call_json
from ncloud.formatting.time_zone import utc_to_local
from ncloud.config import MODELS
from ncloud.formatting.output import print_table


class TrainResults(Command):
    @classmethod
    def parser(cls, subparser):
        train_results = subparser.add_parser("train-results",
                                             help="Retrieve model training "
                                                  "results files: model "
                                                  "weights, callback, "
                                                  "outputs, and neon log.")
        train_results.add_argument("model_id",
                                   help="ID of model to retrieve results of")
        train_results.add_argument("-d", "--directory",
                                   help="Location to download files "
                                        "{directory}/results_files. "
                                        "Defaults to current directory.")
        train_results_mode = train_results.add_mutually_exclusive_group()
        train_results_mode.add_argument("--url", action="store_true",
                                        help="Obtain URLs to directly "
                                             "download individual results.")
        train_results_mode.add_argument("--objects", action="store_true",
                                        help="Download objects directly "
                                             "to specified directory.")
        train_results_mode.add_argument("--zip", action="store_true",
                                        help="Retrieve a zip file of results.")
        train_results_mode.add_argument("--tar", action="store_true",
                                        help="Retrieve a tar file of results.")
        train_results.add_argument("--filter", action='append',
                                   help="Only retrieve files with names "
                                        "matching <filter>.  Note - uses glob "
                                        "style syntax. Multiple --filter "
                                        "arguments will be combined with "
                                        "logical or.")

        train_results.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, filter=None, zip=None, tar=None,
             url=None, objects=None, directory=None):
        vals = dict()
        results_path = os.path.join(MODELS, model_id, "results")
        if filter:
            vals["filter"] = filter

        results = None
        if url or objects:
            vals["format"] = "url"
            results = api_call_json(config, results_path, params=vals)
            if objects:
                directory = directory if directory else '.'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                for result in results["result_list"]:
                    obj = requests.get(result["url"], stream=True)
                    local_file = os.path.join(directory, result["filename"])
                    with open(local_file, 'wb') as f:
                        for chunk in obj.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                return
        elif zip or tar:
            if zip:
                ext = "zip"
                stream = False
            else:
                ext = "tar"
                stream = True
            vals["format"] = ext
            results = api_call(config, results_path, params=vals,
                               stream=stream)
            if results:
                directory = directory if directory else '.'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                filename = (
                    'results_%d_%s.%s' % (
                        int(model_id),
                        datetime.strftime(datetime.today(), "%Y%m%d%H%M%S"),
                        ext
                    )
                )

                with open(os.path.join(directory, filename), 'wb') as f:
                    if stream:
                        for chunk in results.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                        return
                    else:
                        f.write(results)
        else:
            # default to listing results
            vals["format"] = "list"
            results = api_call_json(config, results_path, params=vals)
            if results and 'result_list' in results:
                result_list = results['result_list']
                for result in result_list:
                    result['last_modified'] = \
                        utc_to_local(result["last_modified"])

        return results

    @staticmethod
    def display_after(config, args, res):
        if res and 'result_list' in res:
            if args.url:
                print("Public URLs will expire 1 hour from now.")
            print_table(res['result_list'])
