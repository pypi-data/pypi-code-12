# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Main point of code entry for ncloud.
"""
from ncloud import __version__
from argparse import (ArgumentParser, ArgumentDefaultsHelpFormatter)
from ncloud.config import CMD_NAME, Config
from ncloud.commands.train import TrainModel, StopTraining
from ncloud.commands.list import DatasetList, ListModels, ResourceList
from ncloud.commands.show import DatasetShow, ShowModel
from ncloud.commands.dataset import DatasetUpload, DatasetLink, DatasetRemove
from ncloud.commands.train_results import TrainResults
from ncloud.commands.import_model import ImportModel
from ncloud.commands.predict import Deploy, Undeploy, Predict
from ncloud.commands.predict_list import PredictList
from ncloud.commands.upgrade import Upgrade
from ncloud.commands.configure import Configure


def build_parser(conf):
    parser = ArgumentParser(description=__doc__, prog=CMD_NAME,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--host", default=conf.get_default_host(),
                        help="Nervana cloud host to connect to.")
    parser.add_argument("--api_ver", default=conf.get_default_api_ver(),
                        help="Nervana cloud API version to use.")
    parser.add_argument("--auth_host",
                        default=conf.get_default_auth_host(),
                        help="Nervana host to connect to to perform "
                             "authorization.")
    parser.add_argument("--tenant", default=conf.get_default_tenant(),
                        help="Tenant name to use for requests.")

    subparser = parser.add_subparsers(title="actions")

    Configure.parser(subparser)

    DatasetList.parser(subparser)
    DatasetShow.parser(subparser)
    DatasetUpload.parser(subparser)
    DatasetLink.parser(subparser)
    DatasetRemove.parser(subparser)

    ListModels.parser(subparser)
    ShowModel.parser(subparser)

    TrainModel.parser(subparser)
    TrainResults.parser(subparser)
    StopTraining.parser(subparser)

    ImportModel.parser(subparser)

    Deploy.parser(subparser)
    Undeploy.parser(subparser)
    Predict.parser(subparser)

    PredictList.parser(subparser)

    ResourceList.parser(subparser)

    Upgrade.parser(subparser)

    return parser


def main():
    # import sys
    # print(sys.argv[1:])

    conf = Config()
    parser = build_parser(conf)
    args = parser.parse_args()

    # in python3 argparse subparsers are.... optional :/
    # this is the only time func would not be set
    if not getattr(args, 'func', None):
        parser.error('too few arguments')

    conf.set_default_host(args.host)
    conf.set_default_auth_host(args.auth_host)
    conf.set_default_tenant(args.tenant or '')
    conf.set_default_api_ver(args.api_ver)

    args.func(conf, args)
