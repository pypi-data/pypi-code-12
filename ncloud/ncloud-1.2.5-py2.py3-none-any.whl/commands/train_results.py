# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Subcommands for getting training results.
"""
from __future__ import print_function
import os
from datetime import datetime
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
        train_results_mode.add_argument("--zip", action="store_true",
                                        help="Retrieve a zip file of results.")
        train_results.add_argument("--filter", action='append',
                                   help="Only retrieve files with names "
                                        "matching <filter>.  Note - uses glob "
                                        "style syntax. Multiple --filter "
                                        "arguments will be combined with "
                                        "logical or.")

        train_results.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, model_id, filter=None,
             zip=None, url=None, directory=None):
        vals = dict()
        results_path = os.path.join(MODELS, model_id, "results")
        if filter:
            vals["filter"] = filter

        results = None
        if not url and not zip:
            # default to listing results
            vals["format"] = "list"
            results = api_call_json(config, results_path, params=vals)
            if results and 'result_list' in results:
                result_list = results['result_list']
                for result in result_list:
                    result['last_modified'] = \
                        utc_to_local(result["last_modified"])
        elif url:
            vals["format"] = "url"
            results = api_call_json(config, results_path, params=vals)
        elif zip:
            vals["format"] = "zip"
            resultsfile = api_call(config, results_path, params=vals)
            if resultsfile:
                directory = directory if directory else '.'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                filename = ('results_%d_%s.zip' %
                            (int(model_id),
                             datetime.strftime(datetime.today(),
                                               "%Y%m%d%H%M%S")))
                open(os.path.join(directory, filename), 'wb').write(
                    resultsfile
                )

        return results

    @staticmethod
    def display_after(config, args, res):
        if res and 'result_list' in res:
            if args.url:
                print("Public URLs will expire 1 hour from now.")
            print_table(res['result_list'])
