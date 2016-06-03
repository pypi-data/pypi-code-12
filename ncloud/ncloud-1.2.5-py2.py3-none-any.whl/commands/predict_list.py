# ----------------------------------------------------------------------------
# Copyright 2016 Nervana Systems Inc.
# ----------------------------------------------------------------------------

"""
Subcommands for listing model predictions.
"""

import json
from collections import OrderedDict

from ncloud.commands.command import Command, print_table
from ncloud.config import PREDICTIONS
from ncloud.util.api_call import api_call


class PredictList(Command):
    @classmethod
    def parser(cls, subparser):
        pl = subparser.add_parser(
            "predict-list",
            help="List available predictions for a deployed model."
        )
        pl.add_argument("model_id", help="The deployed model.")
        pl.add_argument(
            "-s", "--status",
            help="Filter results by statuses "
                 "(comma-separated list, case-insensitive)."
        )
        pl.add_argument(
            "-c", "--count",
            help="Return this many results.  Defaults to server default."
        )
        pl.add_argument(
            "-o", "--offset",
            help="Start paging from this offset."
        )
        pl.add_argument(
            "-f", "--formatter", default="table", choices=['table', 'raw'],
            help="Pretty-print results as a table or raw JSON."
        )
        pl.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(
        config, model_id, status=None, count=None, offset=None, formatter=None
    ):
        # "Note that any dictionary key whose value is None will not be added
        # to the URL's query string." -- requests doc
        return api_call(
            config, PREDICTIONS + model_id, method="GET",
            params={'filter': status, 'count': count, 'offset': offset}
        )

    @staticmethod
    def display_after(config, args, res):
        if args.formatter == 'table':
            print_table(json.loads(res, object_pairs_hook=OrderedDict))
            return

        print(res)
