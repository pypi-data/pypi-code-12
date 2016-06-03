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
Command line interface for Nervana's deep learning cloud.
"""
from builtins import object
import inspect
import logging
from argparse import ArgumentTypeError
from ncloud.formatting.output import print_table


logger = logging.getLogger()


def string_argument(string):
    if len(string) > 255:
        raise ArgumentTypeError('"%s" must be less than 255 characters.' %
                                string)
    return string


class Command(object):
    @classmethod
    def parser(cls, subparser):
        raise NotImplementedError("provide a subparser for your command")

    @classmethod
    def arg_names(cls, startidx=1):
        func_args = inspect.getargspec(cls.call).args[startidx:]
        return func_args

    @staticmethod
    def call():
        raise NotImplementedError("provide an implementation for your command")

    @staticmethod
    def display_before(config, args):
        pass

    @staticmethod
    def display_after(config, args, res):
        if res is not None:
            print_table(res)

    @classmethod
    def arg_call(cls, config, args):
        arg_vals = [vars(args)[name] for name in cls.arg_names()]

        cls.display_before(config, args)

        res = cls.call(config, *arg_vals)

        cls.display_after(config, args, res)
